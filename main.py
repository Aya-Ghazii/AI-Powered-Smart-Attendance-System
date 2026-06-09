"""
Main entry point for the Smart Attendance & Security System.

Usage:
  python app/main.py --mode register    # Register a new user
  python app/main.py --mode recognize   # Start recognition loop
  python app/main.py --mode report      # Generate today's report
  python app/main.py --mode test-db     # Test database connection
"""
import sys, os, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def cmd_register():
    from app.registration import register_via_cli
    register_via_cli()


def cmd_recognize():
    from app.recognition import run_recognition
    run_recognition()


def cmd_report():
    from reports.report_generator import generate_pdf_report, generate_excel_report
    generate_pdf_report("daily")
    generate_excel_report("daily")


def cmd_test_db():
    from database.db_config import test_connection
    test_connection()


def main():
    parser = argparse.ArgumentParser(
        description="Smart Attendance & Security System"
    )
    parser.add_argument(
        "--mode",
        choices=["register", "recognize", "report", "test-db"],
        required=True,
        help="Operating mode",
    )
    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════╗
║   AI-Powered Smart Attendance & Security     ║
║   Face Recognition System  v1.0             ║
╚══════════════════════════════════════════════╝
""")

    mode_map = {
        "register":  cmd_register,
        "recognize": cmd_recognize,
        "report":    cmd_report,
        "test-db":   cmd_test_db,
    }
    mode_map[args.mode]()


if __name__ == "__main__":
    main()
