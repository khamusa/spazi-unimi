from dxf_reader import DxfReader
from config_manager import ConfigManager
from json_persistence_manager import JSONPersistenceManager
from db.db_persistence_manager import DBPersistenceManager
from csv_data_updater import CSVDataUpdater
from svg_persistence_decorator import SVGPersistenceDecorator
import sys, re, os, time

class Main():
   def __init__(self):
      self._config      = ConfigManager("config.json")

   def run_command(self, command, files):
      start_time = time.time()

      getattr(self, "run_"+command)(files)

      end_time = time.time() - start_time
      print("Total time     :", end_time , "seconds")

      if len(files):
         print("Arithmetic mean:", end_time / len(files), "seconds")

   def run_dxf(self, files):
      persistence = SVGPersistenceDecorator(JSONPersistenceManager(self._config))
      for filename in files:
         rm = re.match("(\w+)_(\w+)\.dxf", os.path.basename(filename))
         if rm is None:
            raise RuntimeError("File name format error.")

         dx = DxfReader(filename, rm.group(1), rm.group(2))
         persistence.floor_write(dx.floor)

   def run_csv(self, files):
      persistence = DBPersistenceManager(self._config)
      updater = CSVDataUpdater(self._config["csv_headers"], persistence)

      for filename in files:
         with open(filename) as csvfile:
            updater.perform_update(csvfile)

   def run_easy_rooms(self, files_not_used = None):
      print("Easy Rooms Not implemented yet.")

if __name__ == '__main__':
   import argparse

   parser = argparse.ArgumentParser(description = "Programma per l'aggiornamento dati del server Spazi Unimi.")

   parser.add_argument('command', metavar='op', type=str, choices=["csv", "dxf", "easy_rooms"],
                      help="Il commando da eseguire: dxf, csv, easy_rooms")

   parser.add_argument('files', metavar='file', type=str, nargs='*',
                      help='I file su cui lavorare, a seconda del comando scelto. Se il comando è easy_rooms, verrà trascurato.')

   args = parser.parse_args()

   if(args.command in ["csv", "dxf"] and len(args.files) == 0):
      print("Errore: Il comando "+args.command+" richiede almeno un file ."+args.command+" su cui lavorare.\n")
      parser.print_help()
      exit(1)

   if(args.command in ["easy_rooms"] and len(args.files) > 0):
      print("Errore: Il comando "+args.command+" non ammette ulteriori parametri.\n")
      parser.print_help()
      exit(1)

   program = Main()
   program.run_command(args.command, args.files)
