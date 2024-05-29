package workers;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.List;

public class CommandExecutor {

    public static void main(String[] args) {
        // Example usage
        //execute("python", "script.py", "arg1", "arg2");
    }

    public static void execute(List command) {
        try {
            ProcessBuilder processBuilder = new ProcessBuilder(command);
            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();

            // Read output from the command's standard output and error streams asynchronously
            readOutput(process.getInputStream(), "STDOUT");
            readOutput(process.getErrorStream(), "STDERR");

            // Wait for the command to finish execution
            int exitCode = process.waitFor();
            System.out.println("Command executed with exit code: " + exitCode);

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }

    private static void readOutput(final java.io.InputStream inputStream, final String streamType) {
        new Thread(() -> {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println("[" + streamType + "] " + line);
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }).start();
    }
}

