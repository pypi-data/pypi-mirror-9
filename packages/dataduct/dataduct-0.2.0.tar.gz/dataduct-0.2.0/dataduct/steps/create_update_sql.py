"""ETL step wrapper for sql command for inserting into tables
"""
import os
from .transform import TransformStep
from ..database import SqlScript
from ..database import Table
from ..utils import constants as const
from ..utils.helpers import exactly_one
from ..utils.helpers import parse_path
from ..utils.exceptions import ETLInputError


class CreateUpdateSqlStep(TransformStep):
    """Create and Insert step that creates a table and then uses the query to
    update the table data with any sql query provided
    """

    def __init__(self,
                 table_definition,
                 script=None,
                 command=None,
                 analyze_table=True,
                 script_arguments=None,
                 non_transactional=False,
                 **kwargs):
        """Constructor for the CreateUpdateStep class

        Args:
            **kwargs(optional): Keyword arguments directly passed to base class
        """
        if not exactly_one(command, script):
            raise ETLInputError('Both command and script found')

        # Create S3File with script / command provided
        if script:
            update_script = SqlScript(filename=parse_path(script))
        else:
            update_script = SqlScript(command)

        dest = Table(SqlScript(filename=parse_path(table_definition)))

        steps_path = os.path.abspath(os.path.dirname(__file__))
        runner_script = os.path.join(steps_path, const.SQL_RUNNER_SCRIPT_PATH)

        arguments = [
            '--table_definition=%s' % dest.sql().sql(),
            '--sql=%s' % update_script.sql()
        ]

        if analyze_table:
            arguments.append('--analyze')

        if non_transactional:
            arguments.append('--non_transactional')

        if script_arguments is not None:
            if not isinstance(script_arguments, list):
                raise ETLInputError(
                    'Script arguments for SQL steps should be a list')
            arguments.extend(script_arguments)

        super(CreateUpdateSqlStep, self).__init__(
            script=runner_script, script_arguments=arguments,
            no_output=True, **kwargs)

    @classmethod
    def arguments_processor(cls, etl, input_args):
        """Parse the step arguments according to the ETL pipeline

        Args:
            etl(ETLPipeline): Pipeline object containing resources and steps
            step_args(dict): Dictionary of the step arguments for the class
        """
        step_args = cls.base_arguments_processor(etl, input_args)
        cls.pop_inputs(step_args)
        step_args['resource'] = etl.ec2_resource
        return step_args
