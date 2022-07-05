package cgiprot;
#┌─────────────────────────────────
#│  WebProtect用CGI制限モジュール v4.0
#│  cgiprot.cgi - 2011/05/29
#│  Copyright (c) KentWeb
#│  http://www.kent-web.com/
#└─────────────────────────────────
# 【留意事項】
#
# 1. このモジュールは WebProtect (protect.cgi) でCGIをアクセス制限する
#    ためのものです。
# 2. このモジュールは、protect.cgi及びアクセス制限するCGIスクリプトと
#    「必ず」同じディレクトリ内に置いて下さい。
# 3. アスキーモードでFTP転送し、パーミッションは644に設定します。
# 4. アクセス制限したいCGIスクリプトで、
#    require './jcode.pl';
#    の下付近に以下の2行を書き加えます。
#    ---------------------
#    require './cgiprot.cgi';
#    &cgiprot::check;
#    ---------------------
# 5. このモジュールを使用したいかなる不利益・損害等に関して、作者は
#    その責は一切負いません。

#===========================================================
# ■設定項目 : Web Protectのinit.cgiと同じにすること
#===========================================================

# アクセス履歴ファイル
$cf{logfile} = './data/.axslog';

# 認証後の有効時間（分）
# → 初期ログインしてからの有効時間
$cf{job_time} = 60;

# ホスト取得方法
# 0 : gethostbyaddr関数を使わない
# 1 : gethostbyaddr関数を使う
$cf{gethostbyaddr} = 0;

#===========================================================
# ■設定完了
#===========================================================

#-----------------------------------------------------------
#  チェック処理
#-----------------------------------------------------------
sub check {
	# 時間取得
	$ENV{TZ} = "JST-9";
	my $now = time;

	# ホスト名取得
	my $host = &get_host;

	# ログ
	my ($flg,$time);
	open(IN,"$cf{logfile}") || &error("Open Err: $cf{logfile}");
	while (<IN>) {
		my ($id,$date,$hos,$ag,$tim) = split(/<>/);

		if ($host eq $hos) {
			$flg++;
			$time = $tim;
			last;
		}
	}
	close(IN);

	# ホスト情報なし
	if (!$flg) {
		&error("Host not found");
	# 時間切れ
	} elsif ($now - $time > $cf{job_time}*60) {
		&error("Time is Over!");
	}
}

#-----------------------------------------------------------
#  エラー処理
#-----------------------------------------------------------
sub error {
	my $err = shift;

	print <<EOM;
Content-type: text/html

<html>
<body>$err</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  ホスト名取得
#-----------------------------------------------------------
sub get_host {
	my $host = $ENV{'REMOTE_HOST'};
	my $addr = $ENV{'REMOTE_ADDR'};

	if ($cf{gethostbyaddr} && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
	}
	if ($host eq "") { $host = $addr; }

	return $host;
}


1;

