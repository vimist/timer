# Timers

Execute a command when a given time is reached. Start a timer server to begin:

```
$ timers --verbose server 'notify-send Timers {description}'

2022-11-23 20:46:06,362  INFO      Logging level set to INFO
2022-11-23 20:46:06,362  INFO      No pending timers, waiting for request
```

In another terminal:

```
$ timers add Check your emails in 10 minutes
$ timers add Take a break at 1
$ timers list --delta

1:  9m 50s      Check your emails
2:  3h 59m 55s  Take a break
```

You can also remove timers:

```
$ timers remove 1
$ timers list --absolute

1:  13:00:00 24/11/2022  Take a break
```

At 1 o'clock `notify-send Timers 'Take a break'` will be executed and removed
from the list.

Run `timers --help` or `timers <subcommand> --help` for full options.
