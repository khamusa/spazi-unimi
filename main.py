from config_manager import ConfigManager
from tasks import *
from persistence.json_persistence_manager import JSONPersistenceManager
from persistence.db.mongo_db_persistence_manager import MongoDBPersistenceManager
from persistence.svg_persistence_decorator import SVGPersistenceDecorator
from utils.logger import Logger
from model import ORMModel
import time

class Main():
   def __init__(self):
      self._config      = ConfigManager("config/general.json")

   def run_command(self, command, files):
      start_time = time.time()

      getattr(self, "run_"+command)(files)

      end_time = time.time() - start_time
      Logger.success("Total time     :", end_time , "seconds")

      if len(files):
         Logger.success("Arithmetic mean:", end_time / len(files), "seconds")

   def run_dxf(self, files):
      #persistence = SVGPersistenceDecorator(self._config, JSONPersistenceManager(self._config))
      persistence       = MongoDBPersistenceManager(self._config)
      ORMModel.set_pm( persistence )

      task              = DXFTask(self._config)
      task.perform_updates_on_files(files)

   def run_csv(self, files):
      persistence       = MongoDBPersistenceManager(self._config)
      ORMModel.set_pm( persistence )

      task              = CSVTask(self._config)
      task.perform_updates_on_files(files)

if __name__ == '__main__':
   import argparse

   parser = argparse.ArgumentParser(description = "Programma per l'aggiornamento dati del server Spazi Unimi.")

   parser.add_argument('command', metavar='op', type=str, choices=["csv", "dxf", "cow"],
                      help="Il commando da eseguire: dxf, csv")

   parser.add_argument('files', metavar='file', type=str, nargs='*',
                      help='I file su cui lavorare, a seconda del comando scelto.')

   args = parser.parse_args()



   if(args.command in ["csv", "dxf"] and len(args.files) == 0):
      print("Errore: Il comando "+args.command+" richiede almeno un file ."+args.command+" su cui lavorare.\n")
      parser.print_help()
      exit(1)

   if(args.command == 'cow'):
      try:
         with open("assets/cow.txt") as fp:
            for line in fp:
               print(line, end="")
      except:
         print("There is no cow level.")
      exit()

   program = Main()
   program.run_command(args.command, args.files)
