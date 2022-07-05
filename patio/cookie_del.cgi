#!/usr/bin/perl
#Cookieから認証Cookieの値を削除するボタン
# 外部ファイル取り込み
BEGIN {
	require './init.cgi';
	require $jcode;
}
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use HistoryCookie;

&parse_form;
&delete_cookie;

#Cookieから書込IDの値を削除するボタン
sub delete_cookie{
	my $msg = "";
	my $cookie = HistoryCookie->new();
	my $cookie_hist_id = $cookie->get_history_id();
	if($cookie_hist_id eq ''){
		$msg = " 実行しました。";
	}
	if($in{"del_cookie"} eq "on"){
		if($cookie_hist_id){
			$cookie->logout;
			$cookie_hist_id = $cookie->get_history_id();
		}
		$msg = " 実行しました。";
	}
	&header();
	print <<"EOM";
	<form action="./cookie_del.cgi" method="post">
	<input type="hidden" name="del_cookie" value="on">
	<input type="submit" value="書込IDを削除"> $msg
	</form>
</body>
</html>
EOM
	exit;
}