from api import api

if __name__ == '__main__':
   import argparse

   parser = argparse.ArgumentParser(description = 'API Spazi Unimi')
   parser.add_argument('--debug',help='Run server in debug mode',action='store_true',default=False)
   args = parser.parse_args()

   if args.debug:
      api.app.debug = True
   api.app.run()
