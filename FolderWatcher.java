import java.io.IOException;
import java.nio.file.*;

public class FolderWatcher {
    public static void main(String[] args) throws IOException, InterruptedException {
        Path path = Paths.get("./docs");
        WatchService watchService = FileSystems.getDefault().newWatchService();
        path.register(watchService, StandardWatchEventKinds.ENTRY_CREATE);
        
        while (true) {
            WatchKey key = watchService.take();
            for (WatchEvent<?> event : key.pollEvents()) {
                String fileName = event.context().toString();
                // Execute python ingestion script for the newly detected file
                Process p = new ProcessBuilder("./venv/bin/python", "ingest.py", fileName)
                    .inheritIO()
                    .start();
                p.waitFor();
            }
            key.reset();
        }
    }
}
