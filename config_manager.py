import json, os

class ConfigManager:
   """Ottiene le configurazioni utilizzate dal programma da un file json, e
      garantisce che l'environment richiesto per l'esecuzione sia correttamente
      configurato.

      In particolare crea le necessarie cartelle. La configurazione
      diventa disponibile attraverso la subscription notation:

      cm = ConfigManager("config.json")
      cm["folders"]["data"] # returns the data folder relative path
   """

   def __init__(self, config_file):
      with open(config_file) as cf:
         self._config = json.load(cf)

      self._ensure_folders_exist()

   def __getitem__(self, index):
         return self._config[index]

   def _ensure_folders_exist(self):
      for key, value in self["folders"].items():
         try:
            os.makedirs(value)
         except OSError as e: # raised if the folder already exists
            pass
         finally:
            assert os.path.exists(value), "One or more of the"

