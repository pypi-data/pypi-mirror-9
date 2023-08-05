# coding=UTF-8
__copyright__ = "Copyright 2014 Davide Olianas (ubuntupk@gmail.com)."

__license__ = """This f is part of poliBeePsync.
poliBeePsync is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

poliBeePsync is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with poliBeePsync. If not, see <http://www.gnu.org/licenses/>.
"""

from bs4 import BeautifulSoup
from datetime import datetime, timedelta, tzinfo
import requests
import os
import logging
from pyparsing import Word, alphanums, alphas, nums, Group, OneOrMore, \
    Literal, ParseException
from threading import Thread
from signalslot import Signal as sSignal


logger = logging.getLogger("polibeepsync.common")


# --- Custom Exceptions --- #

class InvalidLoginError(Exception):
    """Exception raised when user code, password or both are wrong."""
    def __init__(self):
        pass


# --- Custom Threads --- #
class LoginThread(Thread):
    def __init__(self, user):
        Thread.__init__(self)
        self.name = 'loginthread'
        self.user = user
        self.login_status = sSignal(args=['message'])

    def run(self):
        try:
            self.user.logout()
            self.user.login()
            if self.user.logged is True:
                self.login_status.emit(message='Successful login.')
                logger.info('Successful login.')
        except InvalidLoginError:
            self.user.logout()
            self.login_status.emit(message='Login failed.')
            logger.error("Login failed.", exc_info=True)
        except requests.ConnectionError:
            self.user.logout()
            self.login_status.emit(message='I can\'t connect to the'
                                           ' server. Is the Internet'
                                           ' connection working?')
            logger.error('Connection error.', exc_info=True)
        except requests.Timeout:
            self.user.logout()
            self.login_status.emit(message="The timeout time has been"
                                           " reached. Is the Internet"
                                           " connection working?")
            logger.error("Timeout error.", exc_info=True)


class SyncThread(Thread):
    def __init__(self, user):
        Thread.__init__(self)
        self.name = 'syncthread'
        self.user = user
        self.signal = sSignal(args=['message'])
        self.new = sSignal(args=['course'])
        self.old = sSignal(args=['course'])

    def run(self):
        most_recent = self.user.get_online_courses()
        last = self.user.available_courses
        new = most_recent - last
        removable = last - most_recent
        if len(removable) > 0:
            self.signal.emit(message='The following courses have'
                                     ' been removed because they '
                                     'aren\'t available online: {}'
                             .format(removable))
            for course in removable:
                self.old.emit(course=course)
        if len(new) > 0:
            for course in new:
                course.save_folder_name = course.simplify_name(course.name)
                self.signal.emit(message='A new course '
                                         'was found: {}'.format(course))
                self.new.emit(course=course)
        if len(new) == 0:
            self.signal.emit(message='No new courses found.')
            logger.info('No new courses found.')
        self.user.sync_available_courses(most_recent)
        logger.info('User object changed')


class DownloadThread(object):
    def __init__(self, user, topdir):
        self.user = user
        self.topdir = topdir
        self.download_signal = sSignal(args=['course'])
        self.initial_sizes = sSignal(args=['course'])
        self.data_signal = sSignal(args=['data'])

    def start(self):
        t = Thread(target=self.run)
        t.start()

    def run(self):
        for course in self.user.available_courses:
            subdir = course.save_folder_name
            if course.sync is True:
                try:
                    outdir = os.path.join(self.topdir, subdir)
                    os.makedirs(outdir, exist_ok=True)
                    self.user.update_course_files(course)
                    syncthese = []
                    savedhere = os.path.join(self.topdir,
                                             course.save_folder_name)
                    needsync = need_syncing(course.documents,
                                            savedhere,
                                            syncthese)

                    syncsize = total_size(needsync)
                    print('****SYNCSIZE: ', syncsize)
                    alreadysynced = course.total_file_size - syncsize
                    print('****ALREADYSYNCED ', alreadysynced)
                    course.downloaded_size = alreadysynced
                    print('****DOWNLOADED SIZE setting to ',
                          course.downloaded_size)
                    self.initial_sizes.emit(course=course)

                    self.user.save_files(course, needsync,
                                         self.download_signal,
                                         self.data_signal)
                    # adesso ogni f di syncthese ha la data di download
                    # aggiornata, ma deve essere scritto su f
                    logger.info("Synced files for {}".format(course.name))
                except InvalidLoginError:
                    self.user.logout()
                    logger.info("Login failed.", exc_info=True)
                except requests.ConnectionError:
                    self.user.logout()
                    # self.signal_error.sig.emit('I can\'t connect to'
                    # ' the server. Is the'
                    # ' Internet connection'
                    # ' working?')
                    logger.error('Connection error.', exc_info=True)
                except requests.Timeout:
                    self.user.logout()
                    # self.signal_error.sig.emit("The timeout time has"
                    # " been reached. Is the"
                    # " Internet connection"
                    # " working?")
                    logger.error("Timeout error.", exc_info=True)


# --- "Core" classes here --- #
class GMT1(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=1) + self.dst(dt)

    def dst(self, dt):
        # DST starts last Sunday in March
        d = datetime(dt.year, 4, 1)  # ends last Sunday in October
        self.dston = d - timedelta(days=d.weekday() + 1)
        d = datetime(dt.year, 11, 1)
        self.dstoff = d - timedelta(days=d.weekday() + 1)
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return timedelta(hours=1)
        else:
            return timedelta(0)

    def tzname(self, dt):
        return "GMT +1"


class GenericSet(object):
    def __init__(self):
        self.elements = []

    def _elements_names(self):
        return [elem.name for elem in self.elements]

    def __eq__(self, other):
        this_elements = set(self.elements)
        other_elements = set(other.elements)
        if this_elements == other_elements:
            return True
        else:
            return False

    def __contains__(self, key):
        if key.name in self._elements_names():
            return True
        else:
            return False

    def __getitem__(self, key):
        if key in self._elements_names():
            for elem in self.elements:
                if elem.name == key:
                    return elem
        else:
            raise KeyError

    def __iter__(self):
        return iter(self.elements)

    def __sub__(self, other):
        return list(set(self.elements) - set(other.elements))

    def append(self, *args):
        for elem in args:
            if not self.__contains__(elem):
                self.elements.append(elem)

    def remove(self, arg):
        if arg in self.elements:
            self.elements.remove(arg)

    def __len__(self):
        return len(self.elements)


class Courses(GenericSet):
    def __hash__(self):
        unordered_name = self._elements_names()
        return hash("".join(sorted(unordered_name)))

    def __repr__(self):
        before = "Courses collection:\n"
        texts = [elem.name for elem in self.elements]
        joined_texts = "\n".join(texts)
        return before + joined_texts


class Course(GenericSet):
    def __init__(self, name, documents_url, sync=False):
        logger.debug('Creating course with name={},'
                     ' documents_url={}, sync={}'
                     .format(name, documents_url, sync))
        super(Course, self).__init__()
        self.name = name
        self.documents_url = documents_url
        self.sync = sync
        self.documents = Folder('root', self.documents_url)
        self.save_folder_name = ""
        self.total_file_size = 0  # in bytes
        self.downloaded_size = 0  # in bytes

    def simplify_name(self, name):
        simple = name
        year = Group("[" + OneOrMore(Word(nums, exact=4) +
                                     "-" + Word(nums, exact=2)) + "]")
        no_squared_brackets = Word(
            alphanums,
            ",;.:-_@#°§+*{}^'?=)(/&%$£!\\|\""
        )
        bracketed = Group("[" + OneOrMore(no_squared_brackets) + "]")
        middle = ~bracketed + OneOrMore(Word(alphas))
        try:
            grammar = year.suppress() + Literal("-").suppress() + middle
            simple = " ".join(grammar.parseString(name))
        except ParseException:
            logger.error('Failed to simplify course name {}'.format(name),
                         exc_info=True)
        return simple.title()

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return 'Course {}'.format(self.name)

    def __contains__(self, key):
        if key.name in self._elements_names():
            return True
        else:
            return False

    def __eq__(self, other):
        if self.name == other.name:
            return True
        else:
            return False


class CourseFile(object):
    def __init__(self, name, url, last_online_edit_time):
        gmt1 = GMT1()
        self.name = name
        self.url = url
        self.last_online_edit_time = last_online_edit_time
        self.local_creation_time = None
        self.size = 0  # in bytes

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if os.path.splitext(self.name)[0] == os.path.splitext(other.name)[0]:
            return True
        else:
            return False


class Folder(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.files = []
        self.folders = []

    def __repr__(self):
        return self.name + " folder"

    def __eq__(self, other):
        if self.name == other.name:
            return True
        else:
            return False


def total_size(listoffiles):
    total = 0
    for f, path in listoffiles:
        logger.debug('Size of {}: {} bytes'.format(f.name, f.size))
        total += f.size
    logger.debug('Total size: {}'.format(total))
    return total


def folder_total_size(parentfolder, sizes):
    for f in parentfolder.files:
        print('il f ', f.name, ' è grosso ', f.size)
        print('prima di aggiungere, size è ', sizes)
        sizes.append(f.size)
        print('dopo operazione, size è ', sizes)
    for folder in parentfolder.folders:
        print('sto controllando la dimensione della sottocartella ',
              folder.name)
        folder_total_size(folder, sizes)
        # viene passata sempre la stessa dimensione della cartella più in alto
    return sizes


def synclocalwithonline(local, online):
    """Modifies local in order to reflect changes from online"""
    for f in online.files:
        if f not in local.files:
            local.files.append(f)
        else:
            ind = local.files.index(f)
            local.files[ind].last_online_edit_time = f.last_online_edit_time
    oldfiles = [f for f in local.files if f not in online.files]
    cleanfiles = [f for f in local.files if f not in oldfiles]
    local.files = cleanfiles
    old = [f for f in local.folders if f not in online.folders]
    clean = [f for f in local.folders if f not in old]
    local.folders = clean
    for folder in online.folders:
        if folder not in local.folders:
            local.folders.append(folder)
    for folder in online.folders:
        ind = local.folders.index(folder)
        synclocalwithonline(local.folders[ind], folder)
    return local


def need_syncing(folder, parent_folder, syncthese):
    """Return a flat list with files to download

    Each element is a tuple like this
    (f, path)

    filename is the f as scraped from the web (its name can be with or
    without the extension)
    path is the absolute path of the folder in which the f should be
    downloaded
    """
    print('calling with folder=', folder.name, ', parent folder= ',
          parent_folder, ", lunghezza syncthese = ", len(syncthese))
    # basenames contains the names of files without extension (this is used
    # later because the website sometimes doesn't show the f extension)
    basenames = []
    if os.path.exists(parent_folder):
        basenames = [os.path.splitext(os.path.basename(f))[0]
                     for f in os.listdir(parent_folder)
                     if os.path.isfile(os.path.join(parent_folder, f))]
    for f in folder.files:
        # print(f.local_creation_time, f.last_online_edit_time)
        simplename = os.path.join(parent_folder, f.name)
        if f.local_creation_time is None:
            print('data None')
            syncthese.append((f, parent_folder))
        elif f.local_creation_time < f.last_online_edit_time:
            print('creazione < online')
            syncthese.append((f, parent_folder))
        elif not os.path.exists(simplename) and f.name not in basenames:
            print('scommetto che penso che esistono quelli senza estensione')
            print('f.name = ', f.name)
            print('altrimenti')
            print('non esiste e allora aggiungo')
            syncthese.append((f, parent_folder))
    for f in folder.folders:
        new_parent = os.path.join(parent_folder, f.name)
        need_syncing(f, new_parent, syncthese)
    return syncthese


class User(object):
    loginurl = 'https://beep.metid.polimi.it/polimi/login'
    gmt1 = GMT1()

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.logged = False
        self.subscribed_courses = []
        self.courses_url = ""
        self.available_courses = Courses()
        self.root_save_folder = ""
        self.chunk_download = sSignal(args=['course'])
        # self.chunk_download.connect(self.print_chunk)

    # def print_chunk(self, **kwargs):
    # print(kwargs['chunk_size'])

    def logout(self):
        """Logout.

        It re-creates a session and sets :attr:`logged` to ``False``."""
        del self.session
        self.session = requests.Session()
        # self.session.cookies.clear()
        self.logged = False

    def get_page(self, url):
        """Use this method to get a webpage.

        It will check if the session is expired, and relogin if necessary.

        Returns:
            response (:class:`requests.Response`): a :class:`requests.Response`
            instance
        """
        response = self.session.get(url, timeout=5, verify=True)
        soup = BeautifulSoup(response.text)
        login_tag = soup.find('input', attrs={'id': 'login'})
        if login_tag is not None:
            logger.info("The session has expired. Logging-in again...")
            self.logout()
            self.login()
            response = self.session.get(url, timeout=5, verify=True)
        return response

    def get_file(self, url):
        """Use this method to get a f.

        It will check if the session is expired, and re-login if necessary.
        The f bytes can be accessed with the :attr:`content` attribute

        >>> user = User('username', 'password')
        >>> response = user.get_file('url_to_file', timeout=5, verify=True)
        >>> with open('outfile','wb') as f:
        ...    f.write(response.content)

        Returns:
            response (requests.Response): a :class:`requests.Response` object
        """
        response = self.session.get(url, timeout=5, verify=True, stream=True)
        if len(response.history) > 0:
            # it means that we've been redirected to the login page
            logger.info("The session has expired. Logging-in again...")
            self.logout()
            self.login()
            response = self.session.get(url, timeout=5, verify=True,
                                        stream=True)
        return response

    def _login_first_step(self):
        default_lang_page = self.session.get(self.loginurl, timeout=5,
                                             verify=True)
        lang_soup = BeautifulSoup(default_lang_page.text)
        lang_tag = lang_soup.find('a', attrs={'title': 'English'})
        if lang_tag:
            self.session.get('https://aunicalogin.polimi.it' +
                             lang_tag['href'], timeout=5, verify=True)
        payload = "login=%s&password=%s" % (self.username, self.password) + \
                  '&evn_conferma%3Devento=Accedi'
        login_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:34.0)\
Gecko/20100101 Firefox/34.0',

            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': len(payload),
            'Accept': 'text/html,application/xhtml+xml,\
            application/xml;q=0.9,*/*;q=0.8'
        }
        login_response = self.session.post(
            'https://aunicalogin.polimi.it:443/aunicalogin/\
aunicalogin/controller/IdentificazioneUnica.do?\
&jaf_currentWFID=main',
            data=payload, headers=login_headers)
        return login_response

    def _do_shibboleth(self, first_response):
        hidden_fields = BeautifulSoup(first_response.text).find_all(
            'input', attrs={'type': 'hidden'})
        # The SAML response wants '+' replaced by %2B
        relay_state = hidden_fields[0].attrs['value']
        saml_response = hidden_fields[1].attrs['value'].replace('+',
                                                                '%2B')
        final_request_data = "RelayState=%s&SAMLResponse=%s" % \
                             (relay_state, saml_response)
        final_headers = {
            'Cookie': "GUEST_LANGUAGE_ID=en_GB; \
COOKIE_SUPPORT=true; polij_device_category=PERSONAL_COMPUTER",
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': len(final_request_data),
        }
        self.session.post(
            'https://beep.metid.polimi.it/Shibboleth.sso/SAML2/POST',
            data=final_request_data,
            headers=final_headers)
        cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        for key in cookies:
            if key.startswith('_shibsession'):
                shibsessionstr = "%s=%s" % (key, cookies[key])
        main_headers = {
            'Cookie': "GUEST_LANGUAGE_ID=en_GB; \
COOKIE_SUPPORT=true; polij_device_category=PERSONAL_COMPUTER; %s" %
                      shibsessionstr
        }
        mainpage = self.session.get(
            'https://beep.metid.polimi.it/polimi/login',
            headers=main_headers, timeout=5, verify=True)
        return mainpage

    def login(self):
        """Try logging in.

        If the login is successful, :attr:`logged` is set to ``True``.
        If it fails, :attr:`logged` is set to ``False`` and raises an
        :class:`InvalidLoginError`.

        Raises:
            InvalidLoginError: when the login fails
        """
        # switch to english version if we're on the italian site
        first_response = self._login_first_step()
        login_soup = BeautifulSoup(first_response.text)
        try:
            parenttag = login_soup.find_all('table')[3]
            parenttag.find('td',
                           text='\n\t\t\t\t\t\n\t\t\t\t\t\t\n\t\t\t\t\
\t\tCode: 14 - Identificazione fallita\n\t\t\t\t\t\n\t\t\t\t')
        except IndexError:
            # Usercode and password are ok
            # continue with Shibboleth
            mainpage = self._do_shibboleth(first_response)
            self.courses_url = mainpage.url
            self.logged = True
        else:
            self.logged = False
            raise InvalidLoginError

    def _create_course(self, name, firstlink):
        """Helper function to create a Course with the real URL.

        This is done because the href present in the courses page is a
        redirect to the real page.
        """
        link = self.get_page(firstlink).url
        link = link.rstrip('attivita-online-e-avvisi')
        weird_parameters = [
            '_20_folderId=0',
            '_20_displayStyle=list',
            '_20_viewEntries=0',
            '_20_viewFolders=0',
            '_20_entryEnd=500',
            '_20_entryStart=0',
            '_20_folderEnd=500',
            '_20_folderStart=0',
            '_20_viewEntriesPage=1',
            'p_p_id=20',
            'p_p_lifecycle=0'
            ]
        link = link + 'documenti-e-media?' + "&".join(weird_parameters)
        course = Course(name, link)
        logger.debug('Course found: {}'.format(course.name))
        return course

    def _courses_scraper(self, text):
        """Return a list of tuples containing the courses from the input text.

        Each tuple is (name, firstlink) where "name" is the complete name of
        the course (not stripped of squared brackets) and firstlink is the
        link to be followed in order to get the real course url.
        """
        courses_soup = BeautifulSoup(text)
        raw_courses = courses_soup.find_all('tr',
                                            attrs={'class': 'results-row'})
        # the first tag is not a course
        raw_courses.pop(0)
        # online_courses = Courses()
        # we iterate over the tags
        temporary_courses = []
        # we only need year to parse for real courses
        year = Group("[" + OneOrMore(
            Word(nums, exact=4) + "-" + Word(nums, exact=2)) + "]")
        # bracketed = Group("[" + OneOrMore(Word(printables, " ")) + "]")
        # middle = ~bracketed + OneOrMore(Word(alphas))
        # grammar = year.suppress() + Literal("-").suppress() + middle
        grammar = year
        for course in raw_courses:
            firstlink = course.td.a['href']
            name = course.td.a.strong.text.strip()
            try:
                grammar.parseString(name)
                temporary_courses.append((name, firstlink))
            except ParseException:
                pass
        return temporary_courses

    def get_online_courses(self):
        """Return the courses available online.

        Returns:
            online_courses (:class:`Courses`): a :class:`Courses` container of
            all courses available online."""
        logger.info('Looking for new courses.')
        coursespage = self.get_page(self.courses_url)
        temp_courses = self._courses_scraper(coursespage.text)
        courses = Courses()
        for elem in temp_courses:
            course = self._create_course(elem[0], elem[1])
            courses.append(course)
        return courses

    def sync_available_courses(self, master_courses):
        """Sync :attr:`available_courses` to :attr:`master_courses`.

        This function will compare the courses in master_courses; if some of
        them are not present in the available_courses instance attribute, they
        will be added to available_courses; if any course is present in
        self.available_courses but not in master_courses, it will be
        removed from self.available_courses.

        A typical usage would be the following

        >>> user = User('fakeid', 'fakepwd')
        >>> user.login()
        >>> online = user.get_online_courses()
        >>> user.sync_available_courses(online)

        Args:
            master_courses (Courses): The updated :class:`Courses` instance
        """
        # New courses should be added.
        # the "if not in" check is not really needed, since the append
        # function doesn't allow duplicates.
        for elem in master_courses:
            logger.debug('Comparing course {} with the local copy'
                         'of courses'.format(elem.name))
            if elem not in self.available_courses:
                logger.debug("It's not present in the local copy;"
                             " adding it")
                self.available_courses.append(elem)
        # now do the opposite: if a course has been deleted,
        # do the same with the local copy
        for elem in self.available_courses:
            logger.debug("Comparing course {} from the local data "
                         "to the new list.".format(elem.name))
            if elem not in master_courses:
                logger.debug("It's not present in the new list, "
                             "therefore we remove it from the local"
                             " data")
                self.available_courses.remove(elem)

    def update_course_files(self, course):
        online = self.find_files_and_folders(course.documents_url,
                                             'rootfolder')
        synclocalwithonline(course.documents, online)
        sizes = []
        course.total_file_size = sum(folder_total_size(course.documents,
                                                        sizes))
        print('****DIMENSIONE TOTALE: ', course.total_file_size)

    def find_files_and_folders(self, link, thisfoldername):
        response = self.get_page(link)
        soup = BeautifulSoup(response.text)
        tags = soup.find_all('span', attrs={'class': 'taglib-text'})
        tags = [elem for elem in tags if elem.text != ""]

        tags.pop(0)
        tags.pop(0)
        logger.debug("Tags from which we extract the list of files:"
                     " {}".format(tags))
        rawdates = [elem.parent.parent.parent.next_sibling.next_sibling.
                    next_sibling.next_sibling.next_sibling.next_sibling
                    for elem in tags]
        last_column = [elem.next_sibling.next_sibling.next_sibling.
                       next_sibling for elem in rawdates]

        folder = Folder(thisfoldername, response.url)

        for i, v in enumerate(tags):
            name = v.text
            rawdate = rawdates[i]
            day = int(rawdate.text.split(' ')[1].split('/')[0])
            month = int(rawdate.text.split(' ')[1].split('/')[1])
            year = int('20' + rawdate.text.split(' ')[1].split('/')[2])
            hour = int(rawdate.text.split(' ')[2].split('.')[0])
            minute = int(rawdate.text.split(' ')[2].split('.')[1])
            complete_date = datetime(year, month, day, hour, minute,
                                     tzinfo=self.gmt1)
            download_link = last_column[i].find_all('a')
            elem = download_link[2]
            if elem.text.startswith('  Download ('):
                link = elem['href']
                size = int(float(elem.text.strip()[10:-2].replace(".", "").
                                 replace(",", ".")) * 1024)
                complete_file = CourseFile(name, link, complete_date)
                complete_file.size = size
                folder.files.append(complete_file)

            else:
                link = v.parent['href']
                subfolder = self.find_files_and_folders(link, name)
                folder.folders.append(subfolder)
        return folder

    def save_files(self, course, needsync, downloadsignal, datesignal,
                   chunk_size=512 * 1024):
        for coursefile, path in needsync:
            result = self.get_file(coursefile.url)
            complete_basename = result.headers['Content-Disposition'] \
                .split("; ")[1].split("=")[1].strip('"')
            complete_name = os.path.join(path, complete_basename)
            os.makedirs(path, exist_ok=True)
            with open(complete_name, 'wb') as f:
                logger.info('writing into {}'.format(complete_name))
                for chunk in result.iter_content(chunk_size):
                    if chunk:
                        f.write(chunk)
                        course.downloaded_size += len(chunk)
                        logger.debug('chunk size: {}'.format(len(chunk)))
                        downloadsignal.emit(course=course)
                coursefile.local_creation_time = datetime.now(self.gmt1)
                # we emit another signal here so that we can save to f
                # the updated local creation time
                datesignal.emit(data=(course, coursefile, path))
