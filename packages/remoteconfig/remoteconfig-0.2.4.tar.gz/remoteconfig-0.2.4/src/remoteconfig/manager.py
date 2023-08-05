from localconfig.manager import LocalConfig
import requests

from remoteconfig.utils import url_content


class RemoteConfig(LocalConfig):
  """ A simple wrapper for :class:`localconfig.LocalConfig` to read remote config files with cache option. """

  def __init__(self, last_source=None, cache_duration=None, **localconfig_kwargs):
    """
      :param file/str last_source: Last config source, file or URL. This source is only read when an attempt to read a
                                   config value is made (delayed reading, hence "last") if it exists.
      :param int cache_duration: For URL source only. Optionally cache the URL content for the given duration (seconds) to
                                 avoid downloading too often. This sets the default for all subsequent :meth:`self.read` calls.
      :param dict localconfig_kwargs: Additional keyword args to be passed to localconfig's :meth:`LocalConfig.__init__`
    """

    #: Default cache duration when reading from a URL source
    self._cache_duration = cache_duration

    super(RemoteConfig, self).__init__(last_source, **localconfig_kwargs)

  def read(self, sources, cache_duration=None):
    """
      Queues the config sources to be read later (when config is accessed), or reads immediately if config has already been
      accessed.

      :param file/str/list sources: Config source URL (http/https), source string, file name, or file pointer, or list
                                    of the other sources.  If file source does not exist, it is ignored.
      :param int cache_duration: Default cache durationg for for URL source only. Optionally cache the URL content
                                 for the given duration (seconds) to avoid downloading too often.
                                 This sets the default for all reads now and subsequent reads.
      :return: True if all sources were successfully read or will be read, otherwise False
    """
    if cache_duration is not None:
      self._cache_duration = cache_duration

    return super(RemoteConfig, self).read(sources)

  def _read(self, source):
    """
      Reads and parses the config source

      :param file/str source: Config source URL (http/https), or string, file name, or file pointer.
    """
    if source.startswith('http://') or source.startswith('https://'):
      source = url_content(source, cache_duration=self._cache_duration, from_cache_on_error=True)

    return super(RemoteConfig, self)._read(source)
