#┌─────────────────────────────────
#│ [ WebPatio ]
#│ check.pl - 2006/10/08
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────

#-------------------------------------------------
#  チェックモード
#-------------------------------------------------
sub check {
	&header();
	print <<EOM;
<h3>チェックモード</h3>
<ul>
EOM

	local(%dir) = (
		$logdir, "ログディレクトリ",
		$sesdir, "セッションディレクトリ",
		$upldir, "アップロードディレクトリ",
		$thumbdir, "サムネイル画像ディレクトリ"
	);
	foreach ( keys(%dir) ) {
		if (-d $_) {
			print "<li>$dir{$_}のパス : OK!\n";

			if (-w $_ && -r $_ && -x $_) {
				print "<li>$dir{$_}のパーミッション : OK!\n";
			} else {
				print "<li>$dir{$_}のパーミッション : NG → $_\n";
			}
		} else {
			print "<li>$dir{$_}のパス : NG → $_\n";
		}
	}

	local(%log) = (
		$nowfile,  "現行ファイル",
		$pastfile, "過去ファイル",
		$memfile,  "会員ファイル",
	);
	foreach ( keys(%log) ) {
		if (-f $_) {
			print "<li>$log{$_}のパス : OK!\n";

			if (-w $_ && -r $_) {
				print "<li>$log{$_}のパーミッション : OK!\n";
			} else {
				print "<li>$log{$_}のパーミッション : NG → $_\n";
			}
		} else {
			print "<li>$log{$_}のパス : NG → $_\n";
		}
	}

	print <<EOM;
<li>バージョン : $ver
</ul>
</body>
</html>
EOM
	exit;
}


1;

