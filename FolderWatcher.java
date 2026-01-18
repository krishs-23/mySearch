import java.io.IOException;
import java.nio.file.*;

/**
 * Native Java Watcher to monitor 'docs' folder for new PDF uploads.
 */
public class FolderWatcher {
    public static void main(String[] args) throws IOException, InterruptedException {
        Path path = Paths.get("./docs");
        WatchService watchService = FileSystems.getDefault().newWatchService();
        path.register(watchService, StandardWatchEventKinds.ENTRY_CREATE);
        
        System.out.println("Monitoring: " + path);
        while (true) {
            WatchKey key = watchService.take();
            for (WatchEvent<?> event : key.pollEvents()) {
                System.out.println("New file: " + event.context());
            }
            key.reset();
        }
    }
}
