import java.io.IOException;
import java.nio.file.*;

/** OS-level watcher for automated indexing. */
public class FolderWatcher {
    public static void main(String[] args) throws IOException, InterruptedException {
        Path docPath = Paths.get("./docs");
        WatchService watchService = FileSystems.getDefault().newWatchService();
        docPath.register(watchService, StandardWatchEventKinds.ENTRY_CREATE);

        System.out.println("Monitoring: " + docPath.toAbsolutePath());
        while (true) {
            WatchKey key = watchService.take();
            for (WatchEvent<?> event : key.pollEvents()) {
                Path filename = (Path) event.context();
                new ProcessBuilder("./venv/bin/python", "ingest.py", filename.toString())
                    .inheritIO().start().waitFor();
            }
            if (!key.reset()) break;
        }
    }
}
