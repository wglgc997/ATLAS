import socket
import threading
import time
import urllib.error
import urllib.request
import webbrowser
import uvicorn

HOST = "127.0.0.1"
PORT = 8000

APP_URL = f"http://{HOST}:{PORT}"
HEALTH_URL = f"{APP_URL}/health"


class LinkCheckerLauncher:
    """
    Start and manage the local Link Checker web application.

    The launcher starts the Uvicorn server in a background thread,
    waits until the FastAPI application becomes available, and then
    opens the application in the user's default web browser.
    """
    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        """
        Initialize the launcher configuration.

        Args:
            host: Local address used by the FastAPI server.
            port: Local port used by the FastAPI server.
        """

        self.host = host
        self.port = port
        self.app_url = f"http://{host}:{port}"
        self.health_url = f"{self.app_url}/health"

        self.server: uvicorn.Server | None = None
        self.server_thread: threading.Thread | None = None

    def is_port_available(self) -> bool:
        """
        Check whether the configured network port is available.

            Returns:
                True when the port can be used, otherwise False.
        """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((self.host, self.port))
                return True
            except OSError:
                return False


    def create_server(self) -> uvicorn.Server:
        """
        Create and configure the Uvicorn server.

            Returns:
                A configured Uvicorn Server instance.
        """

        config = uvicorn.Config(
            app="src.web:app",
            host=self.host,
            port=self.port,
            log_level="info",
            reload=False
        )

        return uvicorn.Server(config=config)

    def run_server(self) -> None:
        """
        Run the Uvicorn server.

        This method is executed inside a background thread so the
        launcher can continue checking the application availability.
        """

        if self.server is None:
            raise RuntimeError("The Uvicorn server was not created")

        self.server.run()

    def start_server(self) -> None:
        """
        Start the Uvicorn server in a background thread.

            Raises:
                RuntimeError: If the configured port is already in use.
        """

        if not self.is_port_available():
            raise RuntimeError(
                f"Port {self.port} is already in use."
                "Close the other application and try again."
            )

        self.server = self.create_server()

        self.server_thread = threading.Thread(
            target=self.run_server,
            name="link-checker-server",
            daemon=True,
        )

        self.server_thread.start()


    def wait_until_ready(
        self,
        timeout_seconds: int = 30,
        check_interval_seconds: float = 0.5,
    ) -> bool :
        """
        Wait until the FastAPI health endpoint becomes available.

            Args:
                timeout_seconds: Maximum time to wait for the application.
                check_interval_seconds: Delay between availability checks.

            Returns:
                True when the application is ready, otherwise False.
        """

        deadline = time.monotonic() + timeout_seconds

        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(
                    self.health_url,
                    timeout=2,
                ) as response:
                    if response.status == 200:
                        return True

            except (
                urllib.error.URLError,
                ConnectionError,
                TimeoutError,
            ):
                pass

                time.sleep(check_interval_seconds)

        return False

    def open_browser(self) -> None:
        """
        Open the Link Checker application in the default web browser.
        """
        opened = webbrowser.open_new_tab(self.app_url)

        if not opened:
            print(
                "The browser could not be opened automatically.\n"
                f"Open this address manually: {self.app_url}"
            )

    def stop_server(self) -> None:
        """
        Request a controlled shutdown of the Uvicorn server.
        """

        if self.server is not None:
            self.server.should_exit = True

        if (
            self.server_thread is not None
            and self.server_thread.is_alive()
        ):
            self.server_thread.join(timeout=5)

    def keep_running(self) -> None:
        """
        Keep the launcher active while the server is running.

        The user can stop the application by pressing Ctrl+C or by
        closing the terminal window.
        """

        if self.server_thread is None:
            raise RuntimeError("The server thread was not started.")

        while self.server_thread.is_alive():
            time.sleep(1)

    def run(self) -> None:
        """
        Execute the complete launcher workflow.

        The method starts the server, waits for FastAPI to become
        available, opens the browser, and keeps the application active.
        """

        print("=" * 50)
        print("Link Checker")
        print("=" * 50)
        print("Starting local server...")

        self.start_server()

        if not self.wait_until_ready():
            self.stop_server()

            raise RuntimeError(
                "The Link Checker server did not become available "
                "within the expected time."
            )

        print(f"Application available at: {self.app_url}")
        print("Opening the browser...")
        print("Press Ctrl+C to stop the application.")

        self.open_browser()
        self.keep_running()


def main() -> None:
    """
    Start the Link Checker desktop launcher.
    """
    launcher = LinkCheckerLauncher()

    try:
        launcher.run()

    except KeyboardInterrupt:
        print("\nStopping Link Checker...")

    except RuntimeError as error:
        print(f"\nLauncher error: {error}")
        input("\nPress Enter to close...")

    except Exception as error:
        print(f"\nUnexpected launcher error: {error}")
        input("\nPress Enter to close...")

    finally:
        launcher.stop_server()
        print("Link Checker stopped.")


if __name__ == "__main__":
    main()








