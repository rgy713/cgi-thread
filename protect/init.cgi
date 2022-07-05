# モジュール宣言
use strict;
my %cf;
#┌─────────────────────────────────
#│ WEB PROTECT : init.cgi - 2013/04/06
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────
$cf{version} = 'Web Protect v4.33';
#┌─────────────────────────────────
#│ [注意事項]
#│ 1. このスクリプトはフリーソフトです。このスクリプトを使用した
#│    いかなる損害に対して作者は一切の責任を負いません。
#│ 2. 設置に関する質問はサポート掲示板にお願いいたします。
#│    直接メールによる質問は一切お受けいたしておりません。
#└─────────────────────────────────

#=====================================================================
#  ▼設定項目
#=====================================================================

# 管理用パスワード
$cf{password} = 'pass';

# パスワード発行形態
# 1 : ユーザからの発行＆メンテを可能にする
# 2 : 発行は管理者のみ。ユーザはメンテのみ
# 3 : 発行＆メンテは管理者のみ（index.htmlは不要）
$cf{pwd_regist} = 1;

# 管理者メールアドレス
# → $cf{pwd_regist} = 1; のとき
$cf{master} = 'xxx@xxx.xx';

# sendmailパス【サーバパス】
# → $cf{pwd_regist} = 1; のとき
$cf{sendmail} = '/usr/lib/sendmail';

# sendmailの -fオプション
# → サーバ仕様で必要な場合
$cf{sendm_f} = 0;

# 認証後の有効時間（分）
# → 初期ログインしてからの有効時間
$cf{job_time} = 60;

# 隠しファイル（トップ）
# → ""の中にファイル名のみを記述
${$cf{secret}}[0] = "top.html";

# 以下は隠しファイル（次ページ以降分）
# → [1][2][3]... と続ける。""の中にファイル名のみを記述。
# → CGIの場合はhttp://から記述する。
${$cf{secret}}[1] = "file1.html";
${$cf{secret}}[2] = "file2.html";
${$cf{secret}}[3] = "file3.html";

# バイナリファイル
# → キー（左方）はパラメータ
# → 値（右方）は順に、「ヘッダー」「拡張子」をコンマで区切り
$cf{binary} = {
		gif   => "image/gif,gif",
		jpeg  => "image/jpeg,jpg",
		pdf   => "aplication/pdf,pdf",
		excel => "application/ms-excel,xls",
	};

# 隠しディレクトリ【サーバパス】
# → 外部から直接アクセスできない場所のほうがよい
$cf{prvdir} = './private';

# セッションディレクトリ【サーバパス】
$cf{sesdir} = "./ses";

# パスワードファイル【サーバパス】
$cf{pwdfile} = './data/.htpasswd';

# アクセス履歴ファイル【サーバパス】
$cf{logfile} = './data/.axslog';

# 会員ファイル【サーバパス】
$cf{memfile} = './data/.member';

# テンプレートディレクトリ【サーバパス】
$cf{tmpldir} = "./tmpl";

# 本体プログラムURL【URLパス】
$cf{protect_cgi} = './protect.cgi';

# 入室プログラムURL【URLパス】
$cf{enter_cgi} = './enter.cgi';

# 登録プログラムURL【URLパス】
$cf{manager_cgi} = './manager.cgi';

# 管理プログラムURL【URLパス】
$cf{admin_cgi} = './admin.cgi';

# 最大受理サイズ
# → プログラムとして受理可能なサイズ
# → Byteで指定する [例] 1024 = 1KB
$cf{maxdata} = 10240;

# アクセスログ最大保持数
$cf{max_log} = 300;

# １ページ当り会員表示件数（管理画面）
$cf{pg_max} = 10;

# ユーザ登録アクセス制限（半角スペースで区切る）
#  → 拒否するホスト名又はIPアドレスを記述（アスタリスク可）
#  → 記述例 $deny = '*.anonymizer.com 211.154.120.*';
$cf{deny} = '';

# ホスト取得方法
# 0 : gethostbyaddr関数を使わない
# 1 : gethostbyaddr関数を使う
$cf{gethostbyaddr} = 0;

# パスワード発行形態をユーザ操作にした場合の完了画面の戻り先【URLパス】
$cf{back_url} = "../index.html";

# 新規ユーザー登録間隔（秒）
$cf{wait_regist} = 60;

# 新規ユーザー登録ログファイル
$cf{regist_log} = './data/regist.log';

# 新規ユーザー登録時メールアドレス禁止ワード(中間一致)
# メールアドレスに含むことを禁止する文字列をカンマ区切りで指定します
# (大文字小文字を区別せずに禁止ワードの判定を行います)
$cf{deny_email} = '';

#=====================================================================
#  ▲設定完了
#=====================================================================

# 設定値を返す
sub init {
	return %cf;
}

#-----------------------------------------------------------
#  フォームデコード
#-----------------------------------------------------------
sub parse_form {
	my ($buf,%in);
	if ($ENV{REQUEST_METHOD} eq "POST") {
		&error('受理できません') if ($ENV{CONTENT_LENGTH} > $cf{maxdata});
		read(STDIN, $buf, $ENV{CONTENT_LENGTH});
	} else {
		$buf = $ENV{QUERY_STRING};
	}
	foreach ( split(/&/, $buf) ) {
		my ($key,$val) = split(/=/);
		$key =~ tr/+/ /;
		$key =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;
		$val =~ tr/+/ /;
		$val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;

		# 無効化
		$val =~ s/&/&amp;/g;
		$val =~ s/</&lt;/g;
		$val =~ s/>/&gt;/g;
		$val =~ s/"/&quot;/g;
		$val =~ s/'/&#39;/g;
		$val =~ s/[\r\n]//g;

		$in{$key} .= "\0" if (defined($in{$key}));
		$in{$key} .= $val;
	}
	return %in;
}

#-----------------------------------------------------------
#  エラー画面
#-----------------------------------------------------------
sub error {
	my $err = shift;

	open(IN,"$cf{tmpldir}/error.html") or die;
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!error!/$err/g;

	print "Content-type: text/html\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  crypt暗号
#-----------------------------------------------------------
sub encrypt {
	my ($in) = @_;

	my @wd = ('a'..'z', 'A'..'Z', '0'..'9', '.', '/');
	srand;
	my $salt = $wd[int(rand(@wd))] . $wd[int(rand(@wd))];
	crypt($in, $salt) || crypt ($in, '$1$' . $salt);
}

#-----------------------------------------------------------
#  crypt照合
#-----------------------------------------------------------
sub decrypt {
	my ($in, $dec) = @_;

	my $salt = $dec =~ /^\$1\$(.*)\$/ ? $1 : substr($dec, 0, 2);
	if (crypt($in, $salt) eq $dec || crypt($in, '$1$' . $salt) eq $dec) {
		return 1;
	} else {
		return 0;
	}
}

#-----------------------------------------------------------
#  時間取得
#-----------------------------------------------------------
sub get_time {
	# タイムゾーン設定
	$ENV{TZ} = "JST-9";

	# 時間取得
	my $time = time;
	my ($sec,$min,$hour,$mday,$mon,$year) = (localtime($time))[0..5];

	# フォーマット
	my $date = sprintf("%04d/%02d/%02d-%02d:%02d:%02d",
				$year+1900,$mon+1,$mday,$hour,$min,$sec);

	return ($time,$date);
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

	return ($host,$addr);
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# 著作権表記（削除・改変禁止）
	my $copy = <<EOM;
<p align="center" style="margin-top:3em;font-size:10px;font-family:verdana,helvetica,arial,osaka;">
- <a href="http://www.kent-web.com/" target="_top">WebProtect</a> -
</p>
EOM

	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$copy$2\n";
	} else {
		print "$foot$copy\n";
		print "</body></html>\n";
	}
	exit;
}


1;

