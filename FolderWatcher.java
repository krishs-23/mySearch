import java.io.IOException;
import java.nio.file.*;
public class FolderWatcher {
    public static void main(String[] args) throws IOException, InterruptedException {
        Path path = Paths.get("./docs");
        WatchService ws = FileSystems.getDefault().newWatchService();
        path.register(ws, StandardWatchEventKinds.ENTRY_CREATE);
        while (true) {
            WatchKey key = ws.take();
            for (WatchEvent<?> event : key.pollEvents()) { System.out.println("New file: " + event.context()); }
            key.reset();
        }
    }
}
