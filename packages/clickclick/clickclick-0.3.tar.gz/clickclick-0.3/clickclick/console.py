import click
import datetime
import time


STYLES = {
    'RUNNING': {'fg': 'green'},
    'TERMINATED': {'fg': 'red'},
}


TITLES = {
}

MAX_COLUMN_WIDTH = {
}


def action(msg, **kwargs):
    click.secho(msg.format(**kwargs), nl=False, bold=True)


def ok(msg=' OK', **kwargs):
    click.secho(msg, fg='green', bold=True, **kwargs)


def error(msg, **kwargs):
    click.secho(' {}'.format(msg), fg='red', bold=True, **kwargs)


def warning(msg, **kwargs):
    click.secho(' {}'.format(msg), fg='yellow', bold=True, **kwargs)


def info(msg):
    click.secho('{}'.format(msg), fg='blue', bold=True)


class Action:

    def __init__(self, msg, **kwargs):
        self.msg = msg
        self.msg_args = kwargs
        self.errors = []

    def __enter__(self):
        action(self.msg, **self.msg_args)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            if not self.errors:
                ok()
        else:
            error('EXCEPTION OCCURRED: {}'.format(exc_val))

    def error(self, msg, **kwargs):
        error(msg, **kwargs)
        self.errors.append(msg)

    def progress(self):
        click.secho(' .', nl=False)


def format_time(ts):
    if ts == 0:
        return ''
    now = datetime.datetime.now()
    try:
        dt = datetime.datetime.fromtimestamp(ts)
    except:
        return ts
    diff = now - dt
    s = diff.total_seconds()
    if s > 3600:
        t = '{:.0f}h'.format(s / 3600)
    elif s > 60:
        t = '{:.0f}m'.format(s / 60)
    else:
        t = '{:.0f}s'.format(s)
    return '{} ago'.format(t)


def format(col, val):
    if val is None:
        val = ''
    elif col.endswith('_time'):
        val = format_time(val)
    elif isinstance(val, bool):
        val = 'yes' if val else 'no'
    else:
        val = str(val)
    return val


def print_table(cols, rows):
    colwidths = {}

    for col in cols:
        colwidths[col] = len(TITLES.get(col, col))

    for row in rows:
        for col in cols:
            val = row.get(col)
            colwidths[col] = min(max(colwidths[col], len(format(col, val))), MAX_COLUMN_WIDTH.get(col, 1000))

    for i, col in enumerate(cols):
        click.secho(('{:' + str(colwidths[col]) + '}').format(TITLES.get(col, col.title().replace('_', ' '))),
                    nl=False, fg='black', bg='white')
        if i < len(cols)-1:
            click.secho('│', nl=False, fg='black', bg='white')
    click.echo('')

    for row in rows:
        for col in cols:
            val = row.get(col)
            align = ''
            try:
                style = STYLES.get(val, {})
            except:
                # val might not be hashable
                style = {}
            if val is not None and col.endswith('_time'):
                align = '>'
                diff = time.time() - val
                if diff < 900:
                    style = {'fg': 'green', 'bold': True}
                elif diff < 3600:
                    style = {'fg': 'green'}
            elif isinstance(val, int) or isinstance(val, float):
                align = '>'
            val = format(col, val)

            if len(val) > MAX_COLUMN_WIDTH.get(col, 1000):
                val = val[:MAX_COLUMN_WIDTH.get(col, 1000) - 2] + '..'
            click.secho(('{:' + align + str(colwidths[col]) + '}').format(val), nl=False, **style)
            click.echo(' ', nl=False)
        click.echo('')


def choice(prompt: str, options: list):
    """
    Ask to user to select one option and return it
    """
    click.secho(prompt)
    for i, option in enumerate(options):
        if isinstance(option, tuple):
            value, label = option
        else:
            value = label = option
        click.secho('{}) {}'.format(i+1, label))
    while True:
        selection = click.prompt('Please select (1-{})'.format(len(options)), type=int)
        try:
            result = options[int(selection)-1]
            if isinstance(result, tuple):
                value, label = result
            else:
                value = result
            return value
        except:
            pass


class AliasedGroup(click.Group):
    """
    Click group which allows using abbreviated commands
    """
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))
