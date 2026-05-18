import click
import logic

@click.group()
def cli():
    pass

@cli.command()
def init():
    """אחראי על אתחול מאגר חדש"""
    logic.init()

@cli.command()
@click.argument('path')
def add(path):
    """אחראי על הוספת קבצים ל-staging"""
    logic.add(path)

@cli.command()
@click.option('-m', '--message', required=False,default="No message provided", help='Commit message')
def commit(message):
    """אחראי על יצירת נקודת שמירה (קומיט)"""
    logic.commit(message)

@cli.command()
def status():
    """אחראי על הצגת מצב המאגר הנוכחי"""
    logic.status()

@cli.command()
@click.argument('commit_id')
def checkout(commit_id):
    """אחראי על שחזור גרסה קודמת"""
    logic.checkout(commit_id)

if __name__ == "__main__":
    cli()