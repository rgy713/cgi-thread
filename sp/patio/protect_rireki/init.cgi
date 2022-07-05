# モジュール宣言
use strict;
use Crypt::CBC;
use Crypt::Blowfish;
use File::Basename;
use File::Spec;
use Symbol qw();

use lib qw(./lib);
use Crypt::SaltedHash;
use File::chdir;

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

# このファイルから見たWebPatioフォルダパス
$cf{webpatio_path} = '../';

# 管理用パスワード
$cf{password} = '0123';

# ユーザーパスワード暗号化キー
# 設置場所が異なる場合はこの文字列を変更して下さい
my $user_password_encrypt_key = 'f45hcmfTdUh0TUwX';

# パスワード発行形態
# 1 : ユーザからの発行＆メンテを可能にする
# 2 : 発行は管理者のみ。ユーザはメンテのみ
# 3 : 発行＆メンテは管理者のみ（index.htmlは不要）
$cf{pwd_regist} = 1;

# パスワードファイル【サーバパス】
$cf{pwdfile} = './data/.htpasswd';

# アクセス履歴ファイル【サーバパス】
$cf{logfile} = './data/.axslog';

# 会員ファイル【サーバパス】
$cf{memfile} = './data/.member';

# 書込ID発行ログファイル【サーバパス】
$cf{regist_log} = './data/regist.log';

# テンプレートディレクトリ【サーバパス】
$cf{tmpldir} = "./tmpl";

# 入室プログラムURL【URLパス】
$cf{enter_cgi} = './index.cgi';

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
$cf{gethostbyaddr} = 1;

#=====================================================================
#  ▲設定完了
#=====================================================================

# サーバパス設定値を絶対パスに変換
foreach my $key ('pwdfile', 'logfile', 'memfile', 'regist_log', 'tmpldir') {
	$cf{$key} = File::Spec->rel2abs($cf{$key}, dirname(__FILE__));
}

# WebPatioから動作に必要な設定値を取得
{
	# WebPatio init.cgiによるグローバル汚染を防ぐため、
	# パッケージを一時作成してからrequireして隔離
	package WebPatioConf;
	use File::Basename;
	use File::Spec;
	require File::Spec->catfile(File::Spec->abs2rel(File::Spec->canonpath(dirname(__FILE__) . '/' . $cf{webpatio_path})), 'init.cgi');

	# 書き込み履歴ログファイル分割保存関連パスを
	# このファイルから見た相対パスとなるよう変換
	foreach my $key ('history_logdir', 'history_logdir_number', 'history_logfile_count') {
		$WebPatioConf::history_shared_conf{$key} =
			File::Spec->abs2rel(File::Spec->rel2abs($WebPatioConf::history_shared_conf{$key}, $cf{webpatio_path}));
	}

	# 戻り先URLが相対指定の場合、このファイルから見た相対URLとなるよう変換
	if ($WebPatioConf::history_shared_conf{back_url} !~ /^(?:[a-z]*:\/\/|\/)/i) {
		local $File::chdir::CWD = dirname(__FILE__);
		$WebPatioConf::history_shared_conf{back_url} =
			File::Spec->abs2rel(Cwd::realpath(File::Spec->rel2abs($WebPatioConf::history_shared_conf{back_url}, $cf{webpatio_path})));
	}

	# WebPatio Cookieのキー名の一部に使用するディレクトリパスの取得
	$cf{webpatio_cookie_current_dirpath} = do {
		my $dir_separator_regex = quotemeta(File::Spec->canonpath('/'));
		# ドキュメントルートベースのCGI実行パスを取得し、パスをクリーンにする
		my $tmp_dirpath = dirname(dirname(dirname($ENV{'SCRIPT_NAME'}) . '/' . $cf{webpatio_path}));
		$tmp_dirpath =~ s/(^${dir_separator_regex}?|${dir_separator_regex}?$)//g;
		# URLエンコード
		$tmp_dirpath =~ s/(\W)/'%' . unpack('H2', $1)/eg;
		$tmp_dirpath =~ s/\s/+/g;
		$tmp_dirpath;
	};

	# 設定値取得
	%cf = (%cf, %WebPatioConf::history_shared_conf);

	# WebPatioConfパッケージを削除
	Symbol::delete_package('WebPatioConf');

	# WebPatio ライブラリパス決定
	$cf{webpatio_lib_path} = File::Spec->catfile($cf{webpatio_path}, 'lib');
}

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
#  完了画面
#-----------------------------------------------------------
sub message {
	my ($ttl, $msg, $back_msg, $back_url) = @_;

	# 戻るボタンメッセージ
	if (!defined($back_msg) || $back_msg eq '') {
		$back_msg = 'TOPに戻る';
	}

	# 戻り先URL
	if (!defined($back_url) || $back_url eq '') {
		$back_url = "location.href='$cf{back_url}'";
	} else {
		$back_url = "location.href='$back_url'";
	}

	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/message.html") or &error("open err: message.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# 置き換え
	$tmpl =~ s/!page_ttl!/$ttl/g;
	$tmpl =~ s/!message!/$msg/g;
	$tmpl =~ s/!back_msg!/$back_msg/g;
	$tmpl =~ s/!back_url!/$back_url/g;

	# 表示
	print "Content-type: text/html\n\n";
	&footer($tmpl);
}

#-----------------------------------------------------------
#  crypt暗号
#-----------------------------------------------------------
sub encrypt {
	my ($plaintext) = @_;

	my $cipher = Crypt::CBC->new(
		{
			key    => $user_password_encrypt_key,
			cipher => 'Blowfish'
		}
	);

	return $cipher->encrypt_hex($plaintext);
}

#-----------------------------------------------------------
#  crypt複合
#-----------------------------------------------------------
sub decrypt {
	my ($ciphertext) = @_;

	my $cipher = Crypt::CBC->new(
		{
			key    => $user_password_encrypt_key,
			cipher => 'Blowfish'
		}
	);

	return $cipher->decrypt_hex($ciphertext);
}

#-----------------------------------------------------------
#  ハッシュ化
#-----------------------------------------------------------
sub saltedhash_encrypt {
	my ($plaintext) = @_;

	my $cipher = Crypt::SaltedHash->new(
		algorithm => 'SHA-1'
	);

	$cipher->add($plaintext);
	return $cipher->generate();
}

#-----------------------------------------------------------
#  ハッシュ照合
#-----------------------------------------------------------
sub saltedhash_verify {
	my ($ciphertext, $verify_target) = @_;

	return Crypt::SaltedHash->validate($ciphertext, $verify_target);
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

