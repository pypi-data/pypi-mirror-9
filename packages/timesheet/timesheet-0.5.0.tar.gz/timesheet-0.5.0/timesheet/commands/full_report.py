__author__ = 'vahid'

from timesheet.commands import Command
from timesheet.models import Subject
from timesheet.commands.completers import subject_completer
from prettytable import PrettyTable
from datetime import timedelta


class FullReportCommand(Command):
    name = 'report'
    description = 'Print report about an subject or all subjects'

    @classmethod
    def add_arguments(cls):
        cls.parser.add_argument('subject', nargs='?', help="Subject to do something about that.")\
            .completer = subject_completer

    @staticmethod
    def report_subject(subject):

        print '\n'
        print '%s' % subject.title

        table = PrettyTable(['Task Name', 'Duration', 'From', 'To'])
        table.align["Task Name"] = "l"
        table.align["Duration"] = "c"
        table.padding_width = 1  # default

        total_duration = timedelta()
        for task in subject.tasks:
            total_duration += task.duration
            table.add_row(['' if not task.title else task.title,
                           task.duration_formatted,
                           task.start_time_string,
                           task.end_time_string])

        print table
        print 'Total hours: %.2f' % (total_duration.total_seconds() / 3600.0)
        print

    def do_job(self):
        if self.args.subject:
            subject = Subject.query.filter(Subject.title == self.args.subject).first()
            if not subject:
                print 'Subject can not found: %s' % self.args.subject
            else:
                self.report_subject(subject)
        else:
            for subject in Subject.query.order_by(Subject.entry_time):
                self.report_subject(subject)
