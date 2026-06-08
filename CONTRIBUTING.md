# Contributing to DeepSeek-V3.2-Exp (A-i-developement fork)

This repository is a fork of [deepseek-ai/DeepSeek-V3.2-Exp](https://github.com/deepseek-ai/DeepSeek-V3.2-Exp).

## Upstream

Upstream source: **https://github.com/deepseek-ai/DeepSeek-V3.2-Exp**

This fork tracks the upstream `main` branch and is automatically synchronized daily via the [sync-upstream workflow](.github/workflows/sync-upstream.yml).

## Making Changes

- For bug fixes or improvements to the inference code, open a pull request against the `main` branch of this fork.
- If a change is general enough to benefit the upstream project, please also consider opening a pull request against [deepseek-ai/DeepSeek-V3.2-Exp](https://github.com/deepseek-ai/DeepSeek-V3.2-Exp).

## Syncing with Upstream Manually

If you need to bring in upstream changes ahead of the daily schedule, you can trigger the [Sync Fork with Upstream](.github/workflows/sync-upstream.yml) workflow manually from the Actions tab.

Alternatively, run this locally:

```bash
git remote add upstream https://github.com/deepseek-ai/DeepSeek-V3.2-Exp.git
git fetch upstream
git merge upstream/main
git push origin main
```

## License

This project is licensed under the [MIT License](LICENSE), the same as the upstream repository.
