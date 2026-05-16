import re
from typing import Any, Dict

_PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][\w]*)\.([^\|}]+)(?:\|([^\}]+))?\}")


class ConfigResolvedDict(dict):
    """
    Dictionary that resolves placeholder references within its values.

    String values may reference other parts of the configuration using dot-separated
    paths. Resolution is recursive for dictionaries and lists. Full-string
    placeholders preserve the referenced value's type; interpolated placeholders
    are converted to strings. All references are resolved against the original
    input dictionary.
    """

    def __init__(self, raw_dict: dict[str, Any]):
        self.raw = raw_dict
        self.resolved = self._resolve(self.raw)
        super().__init__(self.resolved)

    def _resolve(self, node):
        """
        Recursively resolve placeholders in strings, dictionaries, and lists.
        Non-container values are returned unchanged.
        """
        if isinstance(node, str):
            return self._resolve_string(node)
        if isinstance(node, dict):
            return {k: self._resolve(v) for k, v in node.items()}
        if isinstance(node, list):
            return [self._resolve(v) for v in node]
        return node

    def _resolve_string(self, value: str) -> Any:
        """
        Resolve placeholders in a string.

        Returns the referenced value directly if the string is a single placeholder
        otherwise interpolates resolved values into the string.
        """
        if not _PLACEHOLDER_RE.search(value):
            return value

        # Check if the entire string is a single placeholder
        if match := _PLACEHOLDER_RE.fullmatch(value):
            dict_name, key_path, _ = match.groups()
            return self._resolve_reference(dict_name, key_path)

        def replacer(match: re.Match) -> str:
            """Handle string interpolation with multiple placeholders"""
            dict_name, key_path, _ = match.groups()
            resolved = self._resolve_reference(dict_name, key_path)
            return str(resolved)

        return _PLACEHOLDER_RE.sub(replacer, value)

    def _resolve_reference(self, dict_name: str, path: str) -> Any:
        """
        Resolve a dot-separated path from a top-level mapping in the raw config.

        Raises KeyError for missing dictionaries or keys, and TypeError when attempting
        to traverse a non-dictionary value.
        """
        try:
            if dict_name not in self.raw:
                raise KeyError(
                    f"Unknown mapping dict '{dict_name}, Available dicts {list(self.raw.keys())}'"
                )

            current = self.raw[dict_name]

            if not isinstance(current, dict):
                raise TypeError(f"Expected dict, got {type(current).__name__}")

            parts = path.split(".")

            if len(parts) == 1:
                if path not in current:
                    raise KeyError(
                        f"Invalid key '{path}, Available keys: {list(current.keys())}'"
                    )
                return current[path]

            for i, part in enumerate(parts):
                if not isinstance(current, dict):
                    raise TypeError(
                        f"Cannot descend into non-dict value at position {i + 1} in path {path}"
                    )
                if part not in current:
                    raise KeyError(
                        f"Key '{part}' not found at position {i + 1} in path '{path}'."
                        f"Available keys: {list(current.keys())}"
                    )
                current = current[part]

            return current

        except (KeyError, TypeError):
            raise


class OneLevelFlatDict(dict):
    """
    A dictionary that normalizes nested mappings to a maximum depth of one
    level below the top-level keys.
    """

    def __init__(self, *args, **kwargs):
        raw = dict(*args, **kwargs)
        super().__init__(self._flatten(raw))

    def _flatten(self, dict_: Dict) -> Dict:
        """
        Flatten the input dictionary so that any nested dictionaries are
        collapsed under their top-level key.
        """
        _out = {}

        for top_key, value in dict_.items():
            if isinstance(value, dict):
                _out[top_key] = self._flatten_children(value)
            else:
                _out[top_key] = value

        return _out

    def _flatten_children(self, d: Dict, prefix: str = "") -> Dict:
        """
        Recursively flatten a nested dictionary using dot-separated keys.
        """
        _result = {}

        for k, v in d.items():
            key = f"{prefix}{k}" if not prefix else f"{prefix}.{k}"

            if isinstance(v, dict):
                _result.update(self._flatten_children(v, key))
            else:
                _result[key] = v

        return _result
