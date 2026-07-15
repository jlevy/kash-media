# kash-media

See the main [kash](https://github.com/jlevy/kash) repo for general instructions.

To run kash with the the media kit features enabled, ensure you have uv set up then:

```shell
uv tool install kash-media --upgrade --force
kash
```

Or for dev builds from within this git repo:

```shell
# Install all deps and run tests:
make
# Run kash with all media kit features enabled:
uv run kash
```

## Model Configuration

This kit inherits the current model profiles from kash-shell. Speaker identification
uses the configurable `fast_llm` workspace parameter instead of requiring a specific
provider. Media transcription uses Deepgram `nova-3` with the newest generally
available batch diarizer through `diarize_model=latest`; it does not send the deprecated
`diarize=true` option. See the main
[model configuration documentation](https://github.com/jlevy/kash#model-configuration)
for the current Anthropic defaults and equivalent OpenAI settings.

Transcription consumes generic `title`, `description`, and `additional_context` item
metadata. Feature-specific hints use the extensible `Item.extra.transcription` mapping:

```yaml
extra:
  transcription:
    key_terms: [Alice Chen, SignalFlow]
    speaker_hints:
      "0": Alice Chen
```

Nova-3 receives each key term separately. Speaker identification uses all descriptive
metadata as untrusted reference context, and explicit speaker hints override model guesses.
Unknown fields in `extra.transcription` are preserved for downstream extensions.

For how to install uv and Python, see [installation.md](docs/installation.md).

For development workflows, see [development.md](docs/development.md).

For instructions on publishing to PyPI, see [publishing.md](docs/publishing.md).

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
