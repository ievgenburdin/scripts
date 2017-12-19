import sys
import urllib.request
import re
from urllib.error import HTTPError


help_message = \
    "Help: \n" \
    "Use format: " \
    "$ python parser.py <start_url> <deep_of_parsing> \n" \
    "Example: " \
    "$ python parser.py <starturl.com> 2 \n" \
    "Script will print new urls.\n" \
    "Finally script will print list of parsed emails."


class Page(object):
    """ Class Page make HTTP request and return found emails and links. """
    def __init__(self, url):
        try:
            http = urllib.request.urlopen(url)
            self.html = http.read()
        except HTTPError:
            self.html = ""
            print("Http error Bad URL:" + url)

    def get_links(self):
        page_str = str(self.html)
        links_list = re.findall(r'<a href=[\'"]?([^\'" >]+)', page_str)
        return [link for link in links_list]

    def get_emails(self):
        page_str = str(self.html)
        email_list = re.findall(r'(\w(?:[-.+]?\w+)+\@(?:[a-zA-Z0-9](?:[-+]?\w+)*\.)+[a-zA-Z]{2,})', page_str)
        return [email for email in email_list]


class EmailParser(object):
    """
    Main class whose objects parses and print data from page.

    structure_dict = {
        'level-1':{'links': ['<link-1>', '<link-1>', '<link-1>', ..., '<link-N>',],
                   'emails': [<email-1>, <email-2>, <email-3>, ..., <email-N>]
                  },
        'level-2':{'links': ['<link-1>', '<link-1>', '<link-1>', ..., '<link-N>',],
                   'emails': [<email-1>, <email-2>, <email-3>, ..., <email-N>]
                  },
        '  ...  ':{'links': ['<link-1>', '<link-1>', '<link-1>', ..., '<link-N>',],
                   'emails': [<email-1>, <email-2>, <email-3>, ..., <email-N>]
                  },
        'level-N':{'links': ['<link-1>', '<link-1>', '<link-1>', ..., '<link-N>',],
                   'emails': [<email-1>, <email-2>, <email-3>, ..., <email-N>]
                  }
    }

    url = string, format: http://www.example.com
    deep = integer
    """
    def __init__(self, url, deep):
        self.url = url
        self.deep = int(deep)
        self.structure_dict = {str(i): {'links': [], 'emails': []} for i in range(0, self.deep + 1)}

    def parse(self):
        for i in sorted(self.structure_dict.keys()):
            if i == str(0):
                page = Page(self.url)
                print("Link " + self.url + "was started")
                links = page.get_links()
                emails = page.get_emails()
                self.add_to_structure(i, links, emails)

            else:
                for link in self.structure_dict[str(int(i)-1)]['links']:
                    print("Link " + self.url + link + "was started")
                    page = Page(self.url + link)
                    links = page.get_links()
                    emails = page.get_emails()
                    self.add_to_structure(i, links, emails)
                    print("Link " + self.url + link + "was done")

    def add_to_structure(self, i, links, emails):
        new_links = []
        new_emails = []
        for i_link in range(0, len(links)):
            new_links = self.clean_items(links, int(i), 'links')
        for i_email in range(0, len(emails)):
            new_emails = self.clean_items(emails, int(i), 'emails')
        self.structure_dict[i]['links'] += new_links
        self.structure_dict[i]['emails'] += new_emails

    def clean_items(self, items, max_level, type_items):
        unique_items = []
        for i in range(0, max_level+1):
            unique_items = list(set(items) - set(self.structure_dict[str(i)][type_items]))
        return unique_items

    def print_emails(self):
        for key in sorted(self.structure_dict.keys()):
            for email in self.structure_dict[key]['emails']:
                print(email)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] and sys.argv[2]:
        parser = EmailParser(sys.argv[1], sys.argv[2])
        parser.parse()
        parser.print_emails()
        print("Success")

    else:
        print(help_message)
