# encoding: utf-8

import os
import shutil
import static_bundle
from static_bundle.utils import write_to_file, copy_file


class Asset(object):
    """
    Asset / Build group type
    Bundles in different build groups can be minified or prepared with different methods
    Objects has a fluent interface

    :param name: unique name of build group in bundle
    :param multitype: When multitype disabled, bundles will be checked for all having same type
        for example JS or CSS
    :param minify: Use minify with [minifier]

    :type builder: StandardBuilder
    :type name: str|unicode
    :type minifier: static_bundle.minifiers.DefaultMinifier
    :type multitype: bool
    :type minify: bool
    :type files_encoding: str
    """

    def __init__(self, builder, name,
                 minifier=None, multitype=False,
                 minify=False, merge=False,
                 merge_out_file=None, files_encoding="utf-8"):
        self.builder = builder
        self.name = name
        self.multitype = multitype
        self.minify = minify or minifier is not None
        self.minifier = minifier
        self.files_encoding = files_encoding
        self.merge = merge
        self.merge_out_file = merge_out_file

        self.bundles = []
        self.files = []

    def add_bundle(self, *args):
        """
        Add some bundle to build group

        :type bundle: static_bundle.bundles.AbstractBundle
        @rtype: BuildGroup
        """
        for bundle in args:
            if not self.multitype and self.has_bundles():
                first_bundle = self.get_first_bundle()
                if first_bundle.get_type() != bundle.get_type():
                    raise Exception(
                        'Different bundle types for one Asset: %s[%s -> %s]'
                        'check types or set multitype parameter to True'
                        % (self.name, first_bundle.get_type(), bundle.get_type())
                    )
            self.bundles.append(bundle)
        return self

    def collect_files(self):
        """
        Return collected files links

        :rtype: list[static_bundle.files.StaticFileResult]
        """
        self.files = []
        for bundle in self.bundles:
            bundle.init_build(self, self.builder)
            bundle_files = bundle.prepare()
            self.files.extend(bundle_files)
        return self

    def get_minifier(self):
        """
        Asset minifier
        Uses default minifier in bundle if it's not defined

        :rtype: static_bundle.minifiers.DefaultMinifier|None
        """
        if self.minifier is None:
            if not self.has_bundles():
                raise Exception("Unable to get default minifier, no bundles in build group")
            minifier = self.get_first_bundle().get_default_minifier()
        else:
            minifier = self.minifier
        if minifier:
            minifier.init_asset(self)
        return minifier

    def has_bundles(self):
        return len(self.bundles) > 0

    def get_first_bundle(self):
        return self.bundles[0]

    def enable_minify(self):
        self.minify = True
        return self

    def disable_minify(self):
        self.minify = False
        return self


class StandardBuilder(object):
    """
    Builder
    Provide build / collect links strategy for static files

    :type config: static_bundle.configs.BuilderConfig
    """

    def __init__(self, config):
        self.config = config
        self.assets = {}

    def create_asset(self, name, **kwargs):
        """
        Create asset

        :type name: unicode|str
        :rtype: Asset
        """
        asset = Asset(self, name, **kwargs)
        self.assets[name] = asset
        return asset

    def remove_asset(self, name):
        """
        Remove asset by name

        :type name: unicode|str
        """
        if name in self.assets:
            del self.assets[name]

    def get_asset(self, name):
        """
        Get asset by name

        :type name: unicode|str
        """
        assert self.has_asset(name), "Asset is not created yet, use has_asset for checking"
        return self.assets[name]

    def has_asset(self, name):
        """
        Check asset exists by name

        :type name: unicode|str
        """
        return name in self.assets

    def render_asset(self, name):
        """
        Render all includes in asset by names

        :type name: str|unicode
        :rtype: str|unicode
        """
        result = ""
        if self.has_asset(name):
            asset = self.get_asset(name)
            if asset.files:
                for f in asset.files:
                    result += f.render_include() + "\r\n"
        return result

    def render_include_group(self, name):
        """
        Alias for render_asset method
        """
        return self.render_asset(name)

    def collect_links(self, env=None):
        """
        Return links without build files
        """
        for asset in self.assets.values():
            if asset.has_bundles():
                asset.collect_files()
        if env is None:
            env = self.config.env
        if env == static_bundle.ENV_PRODUCTION:
            self._minify(emulate=True)
        self._add_url_prefix()

    def make_build(self):
        """
        Move files / make static build
        """
        for asset in self.assets.values():
            if asset.has_bundles():
                asset.collect_files()
        if not os.path.exists(self.config.output_dir):
            os.makedirs(self.config.output_dir)
        if self.config.copy_only_bundles:
            for asset in self.assets.values():
                if not asset.minify and asset.files:
                    for f in asset.files:
                        copy_file(f.abs_path, self._get_output_path(f.abs_path))
        else:
            copy_excludes = {}
            for asset in self.assets.values():
                if asset.minify and asset.files:
                    for f in asset.files:
                        copy_excludes[f.abs_path] = f
            for root, dirs, files in os.walk(self.config.input_dir):
                for fpath in files:
                    current_file_path = os.path.join(root, fpath)
                    if current_file_path not in copy_excludes:
                        copy_file(current_file_path, self._get_output_path(current_file_path))
        self._minify()

    def clear(self, exclude=None):
        """
        Clear build output dir
        :type exclude: list|None
        """
        exclude = exclude or []
        for root, dirs, files in os.walk(self.config.output_dir):
            for f in files:
                if f not in exclude:
                    os.unlink(os.path.join(root, f))
            for d in dirs:
                if d not in exclude:
                    shutil.rmtree(os.path.join(root, d))

    def _get_output_path(self, path):
        return path.replace(self.config.input_dir, self.config.output_dir, 1)

    def _minify(self, emulate=False):
        for asset in self.assets.values():
            if asset.minify and asset.files:
                asset_minifier = asset.get_minifier()
                if asset_minifier:
                    if asset.merge:
                        bundle = asset.get_first_bundle()
                        asset_file = bundle.get_file_cls()
                        if asset.merge_out_file:
                            asset_file_abs_path = os.path.join(self.config.output_dir, asset.merge_out_file)
                            asset_file_rel_path = asset.merge_out_file
                        else:
                            asset_file_abs_path = None
                            asset_file_rel_path = None
                            for b in asset.bundles:
                                if asset_file_abs_path is None:
                                    asset_file_abs_path = b.abs_bundle_path
                                elif asset_file_abs_path != b.abs_bundle_path:
                                    raise Exception('Can\'t merge file with different bundle dirs, '
                                                    'define the merge_out_file Asset property')
                                if asset_file_rel_path is None:
                                    asset_file_rel_path = b.rel_bundle_path
                                elif asset_file_rel_path != b.rel_bundle_path:
                                    raise Exception('Can\'t merge file with different bundle dirs, '
                                                    'define the merge_out_file Asset property')
                            asset_file_name = asset.name + "." + bundle.get_extension()
                            asset_file_abs_path = os.path.join(self._get_output_path(asset_file_abs_path), asset_file_name)
                            asset_file_rel_path = asset_file_rel_path + '/' + asset_file_name
                        if not emulate:
                            text = asset_minifier.before()
                            for f in asset.files:
                                text = asset_minifier.contents(f, text)
                            text = asset_minifier.after(text)
                            dirname = os.path.dirname(asset_file_abs_path)
                            if not os.path.exists(dirname):
                                os.makedirs(dirname)
                            write_to_file(asset_file_abs_path, text, asset.files_encoding)
                        asset.files = [asset_file(asset_file_rel_path, asset_file_abs_path)]
                    elif not emulate:
                        for f in asset.files:
                            text = asset_minifier.before()
                            text = asset_minifier.contents(f, text)
                            text = asset_minifier.after(text)
                            out_path = self._get_output_path(f.abs_path)
                            dirname = os.path.dirname(out_path)
                            if not os.path.exists(dirname):
                                os.makedirs(dirname)
                            write_to_file(out_path, text, asset.files_encoding)
                else:
                    static_bundle.logger.warning("Minifier is not defined for asset. Skipped.")

    def _add_url_prefix(self):
        for asset in self.assets.values():
            if asset.files:
                for file_result in asset.files:
                    file_result.rel_path = self.config.url_prefix + file_result.rel_path.lstrip('/')