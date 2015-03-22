from utils          import ConfigManager
from tasks          import CSVTask, DXFTask, SVGTask
from persistence    import MongoDBPersistenceManager
from utils.logger   import Logger
from model.odm      import ODMModel
import time

class Main():
   """
   Main class, is the entry point of the application.
   """

   def __init__(self):
      self._config      = ConfigManager("config/general.json")

   def run_command(self, command, files):
      """
      Call a command and pass the files we want to process.

      Arguments:
      - command: name of the command we want to run;
      - files: files we want to process.

      Returns: None

      The command name will be used to call the respective routine in the Main
      class. Using the time library to calculate the total time an the mean of
      execution.
      """
      start_time = time.time()

      getattr(self, "run_"+command)(files)

      end_time = time.time() - start_time
      Logger.success("Total time     :", end_time , "seconds")

      if len(files):
         Logger.success("Arithmetic mean:", end_time / len(files), "seconds")

   def run_dxf(self, files):
      """
      Process dxf files.

      Arguments:
      - files: files we want process.

      Returns: None

      Instantiates a MongoDBPersistenceManager and a DXFTask to process the dxf
      files whit the apposite procedure.
      """
      persistence       = MongoDBPersistenceManager(self._config)
      ODMModel.set_pm( persistence )

      task              = DXFTask(self._config)
      task.perform_updates_on_files(files)

   def run_csv(self, files):
      """
      Process csv files.

      Arguments:
      - files: files we want process.

      Returns: None

      Instantiates a MongoDBPersistenceManager and a CSVTask to process the csv
      files whit the apposite procedure.
      """
      persistence       = MongoDBPersistenceManager(self._config)
      ODMModel.set_pm( persistence )

      task              = CSVTask(self._config)
      task.perform_updates_on_files(files)

   def run_svg(self, b_ids):
      """
      Create svg files representing maps of buildings.

      Arguments:
      - b_ids: a list of string representing the building ids of the buildings
      we want create/update svg files.

      Returns: None

      Instantiates a MongoDBPersistenceManager and a SVGTask to create the svg
      files whit the apposite procedure.
      If b_ids is None the CSVTask create svg files of every building in the DB.
      """
      persistence       = MongoDBPersistenceManager(self._config)
      ODMModel.set_pm( persistence )

      task              = SVGTask(self._config)
      task.perform_svg_update(b_ids)

if __name__ == '__main__':
   """
   Main procedure of the application, parse the arguments and call the
   run_command function passing the command we want execute and the files we
   want process.
   """
   import argparse

   parser = argparse.ArgumentParser(description = "Programma per l'aggiornamento dati del server Spazi Unimi.")

   parser.add_argument('command', metavar='op', type=str, choices=["csv", "dxf", "svg", "cow"],
                      help="Il commando da eseguire: dxf, csv, svg")

   parser.add_argument('files', metavar='file', type=str, nargs='*',
                      help='I file su cui lavorare, a seconda del comando scelto.')

   args = parser.parse_args()

   # Development mode
   from tasks.mergers import DataMerger
   DataMerger.skip_geocoding = True

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
