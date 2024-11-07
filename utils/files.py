import os
import time

class Files:
    
    def __init__(self):
        print(f'Class: {self.__class__.__name__} - constructor')
        self.initial_list = None

    def ensure_directory_exists(self, file_path):
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def download_file_prepare(self):
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.initial_list = os.listdir(download_dir)
        
    def get_downloaded_file(self, timeout=10):
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        min_file_size = 1024  # Defina o tamanho mínimo do arquivo (1 KB)

        # Loop para verificar se um novo arquivo foi baixado
        start_time = time.time()
        while True:
            current_list = os.listdir(download_dir)
            # Verifica se há novos arquivos na lista
            new_files = [f for f in current_list if f not in self.initial_list]

            # Filtra novos arquivos que não são temporários ou muito pequenos
            valid_files = [
                f for f in new_files
                if not f.endswith('.tmp') and os.path.getsize(os.path.join(download_dir, f)) >= min_file_size
            ]

            if valid_files:
                new_file = valid_files[0]
                print(f'Novo arquivo baixado: {new_file}')

                new_file_path = os.path.join(download_dir, new_file)
                while True:
                    if os.path.exists(new_file_path):
                        try:
                            with open(new_file_path, 'rb') as f:
                                break
                        except IOError:
                            time.sleep(0.5)
                    else:
                        time.sleep(0.5)

                return new_file_path
            if time.time() - start_time > timeout:
                return None

            
            time.sleep(0.5)