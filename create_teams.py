import sys
import random
import copy

from CTFd import create_app
from CTFd.models import db, Teams
from CTFd.utils.crypto import hash_password

app = create_app()

def insert_team(name, region, key=None):
  existing_team = Teams.query.filter_by(name=name).first()  

  if key is None:
    key = '%064x' % random.randrange(16**64)
  if existing_team:
    print('Updated team ' + name + ' with password ' + key)
    existing_team.region = region
    existing_team.password = hash_password(key)
    return key, existing_team
  else:
    print('Created team ' + name + ' with password ' + key)
    team = Teams(name=name, region=region, password=key)

    return key, team


def get_teams():
  with open('./teams.csv', 'r') as f:
    for l in f.readlines():
      l = l.strip()
      vals = [s.strip() for s in l.split(', ')]
      if len(vals) == 2:
        [name, region] = vals
        yield(name, region)
      
def write_teams(teams):
  with open('generated.csv', 'w+') as f:
    for password, team in teams:
      f.write(', '.join([team.name, password]) + '\n')


def main():
  teams = get_teams()

  created = []

  with app.app_context():
    if len(sys.argv) == 2:
      p, team = insert_team(sys.argv[1], 'root')
      db.session.add(team)
      db.session.commit()
    elif len(sys.argv) == 3:
      p, team = insert_team(sys.argv[1], 'root', key=sys.argv[2])
      db.session.add(team)
      db.session.commit()
    else:
      for name, region in teams:
        password, team = insert_team(name, region)

        db.session.add(team)

        created.append((password, team))

      write_teams(created)
      db.session.commit()
  
if __name__ == '__main__':
  main()