import sys
import random
import copy

from CTFd import create_app
from CTFd.models import db, Teams, Users
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
    team = Teams(name=name, region=region, password=key, hidden=1)

    return key, team

# 156 is root region
def create_user(region):
  key = '%064x' % random.randrange(16**64)
  user = Users(name=region + ' admin', password=key, team_id=156)
  print('Created team ' + region + ' admin' + ' with password ' + key)
  return key, user

def main():
  created = []

  with app.app_context():
    regions = ['CSAW US-Canada', 'CSAW Mexico', 'CSAW Europe', 'CSAW MENA', 'CSAW Israel', 'CSAW India']
    for region in regions:
      key, user = create_user(region)
      created.append((region + ' admin', key))
      db.session.add(user)

    db.session.commit()

    with open('admin_prod_regions.csv', 'w+') as f:
      for region, k in created: 
        f.write(f'{region}, {k}\n')
  
if __name__ == '__main__':
  main()