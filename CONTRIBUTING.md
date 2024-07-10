# Contribution Guidelines

We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Pull Requests

We actively welcome your pull requests.

### For new features

1. Create a Github issue proposing a new feature and make sure it doesn't exist yet.
2. Fork the repo and create your branch from `main`
3. Issue a pull request
4, Address any feedback in code review promptly

### For bug fixes

A great way to contribute to the project is to send a detailed issue when you encounter a problem. We always appreciate a well-written, thorough bug report.

1. Review the existing issues
2. Create a new issue if the bug doesn't have a corresponding one yet
3. Issue a pull request specifying the introduced changes

## License

By contributing, you agree that your contributions will be licensed under the project's license, which is MIT. You can find more details in the **LICENSE.md** file.

## Development - Contributing

If you already cloned the repository and you want to start contributing, we have provided the `dev.sh` script to make things easier and compatible.
So you can get all that you need by using any of the following commands:

### Start the development environment

```bash
bash dev.sh start
```

### Restart the environment

```bash
bash dev.sh restart
```

### Shutdown the environment

```bash
bash dev.sh shutdown
```

**Note**: Some of the above utilities accepts certain parameters, you can display the usage/help message via the `--help` flag:

```bash
bash dev.sh [ start | restart | shutdown ] --help
```

The development environment creates and runs the following services:
- API - FastAPI
- Client - Vue.js dev server
- External memory - Redis