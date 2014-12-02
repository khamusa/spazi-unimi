from tasks.dxf.dxf_reader import DxfReader
from config_manager import ConfigManager
from persistence.json_persistence_manager import JSONPersistenceManager
from persistence.db.mongo_db_persistence_manager import MongoDBPersistenceManager
from tasks.csv_data_updater import CSVDataUpdater
from persistence.svg_persistence_decorator import SVGPersistenceDecorator
from utils.logger import Logger
import sys, re, os, time, shutil

class Main():
   def __init__(self):
      self._config      = ConfigManager("config.json")

   def save_file(self, file, dest, name):
      shutil.copy(file, dest + "/" + name)

   def run_command(self, command, files):
      start_time = time.time()

      getattr(self, "run_"+command)(files)

      end_time = time.time() - start_time
      print("Total time     :", end_time , "seconds")

      if len(files):
         print("Arithmetic mean:", end_time / len(files), "seconds")

   def run_dxf(self, files):
      persistence = SVGPersistenceDecorator(self._config, JSONPersistenceManager(self._config))
      # TO-DO creare DXFDataUpdater
      for filename in files:
         rm = re.match("(\w+)_(\w+)\.dxf", os.path.basename(filename))
         if rm is None:
            print("File name format error: ", filename)
            continue

         try:
            dx = DxfReader(filename, rm.group(1), rm.group(2))
         except Exception:
            Logger.error("File processing was not completed: " + filename)
            continue
         persistence.floor_write(dx.floor)
         Logger.info("Completed - {} rooms founded in: {}".format(dx.floor.n_rooms, filename))
   def run_csv(self, files):
      persistence = MongoDBPersistenceManager(self._config)
      updater = CSVDataUpdater(self._config["csv_headers"], persistence)

      for filename in files:
         Logger.info("Processing file " + filename)
         with open(filename) as csvfile:
            csv_name = updater.perform_update(csvfile)
            if csv_name is not None:
               self.save_file(filename, self._config["folders"]["data_csv_sources"], csv_name + ".csv")

   def run_easy_rooms(self, files_not_used = None):
      print("Easy DrawableRooms Not implemented yet.")

if __name__ == '__main__':
   import argparse

   parser = argparse.ArgumentParser(description = "Programma per l'aggiornamento dati del server Spazi Unimi.")

   parser.add_argument('command', metavar='op', type=str, choices=["csv", "dxf", "easy_rooms", "cow"],
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
