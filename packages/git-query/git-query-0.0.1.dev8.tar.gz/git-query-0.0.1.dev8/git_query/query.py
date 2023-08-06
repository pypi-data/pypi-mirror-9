from dateutil import parser

from git_query import api
from git_query import constants

from prettytable import PrettyTable


class App(object):

    def __init__(self):
        self.gerrit = api.Gerrit(constants.USERNAME, constants.TOKEN)
        self.git = api.Git()
        self.data = self.gerrit.changes({
            'q': 'status:open+project:' + self.git.repo_name
        })

    def show_all(self):
        table = PrettyTable([
            '?',
            'Id',
            'Branch',
            'Owner',
            'Subject',
            'Modified'
        ])
        table.align['Subject'] = 'l'
        for item in self.data:
            updated = parser.parse(item['updated'])
            if item['change_id'] in self.git.change_ids:
                flag = '+'
            else:
                flag = ' '

            table.add_row([
                flag,
                item['_number'],
                item['branch'],
                item['owner']['name'].split(' ')[0],
                item['subject'][:max(
                    constants.TERM_WIDTH - constants.MIN_WIDTH, 0)],
                updated.strftime('%b %d %H:%M')
            ])
        print(table)

    def show_id(self, id):
        for item in self.data:
            if item['_number'] == int(id):
                self.parse_item(item)
                break

    def parse_item(self, item):
        table = PrettyTable(['Property', 'Value'])
        table.align['Property'] = 'l'
        table.align['Value'] = 'l'

        # processing
        del item['id']
        item['owner'] = item['owner']['name']
        item['created'] = parser.parse(item['created']).strftime('%b %d %Y %H:%M')
        item['updated'] = parser.parse(item['updated']).strftime('%b %d %Y %H:%M')
        table.add_row([
            'gerrit_url', constants.HOST + '/' + str(item['_number'])])
        for key in item:
            table.add_row([key, item[key]])

        table.add_row([
            'local_branches',
            self.git.change_ids.get(item['change_id'])
        ])
        print(table)

    def show_current(self):
        change_id = self.git.getChangeId(None)
        for item in self.data:
            if change_id and item['change_id'] == change_id:
                self.parse_item(item)
                break
