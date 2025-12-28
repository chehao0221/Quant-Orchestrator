from core import GuardianEngine, Notifier

def main():
    engine = GuardianEngine()
    notifier = Notifier()

    payload = engine.run()
    notifier.send(payload)

if __name__ == "__main__":
    main()
