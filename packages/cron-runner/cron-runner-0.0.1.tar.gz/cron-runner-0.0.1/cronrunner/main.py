from commandr import Run, command
import registry


@command("run")
def run(name, debug=False, dryrun=False, configfile="/etc/cron-runner.yaml"):
    registry.debug = debug
    registry.dryrun = dryrun
    registry.init_config(configfile)

    from cron import Cron

    job = Cron()
    job.run(name)


def main():
    Run()


if __name__ == "__main__":
    main()
