#!/usr/bin/perl
#Cookie����F��Cookie�̒l���폜����{�^��
# �O���t�@�C����荞��
BEGIN {
	require './init.cgi';
	require $jcode;
}
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use HistoryCookie;

&parse_form;
&delete_cookie;

#Cookie���珑��ID�̒l���폜����{�^��
sub delete_cookie{
	my $msg = "";
	my $cookie = HistoryCookie->new();
	my $cookie_hist_id = $cookie->get_history_id();
	if($cookie_hist_id eq ''){
		$msg = " ���s���܂����B";
	}
	if($in{"del_cookie"} eq "on"){
		if($cookie_hist_id){
			$cookie->logout;
			$cookie_hist_id = $cookie->get_history_id();
		}
		$msg = " ���s���܂����B";
	}
	&header();
	print <<"EOM";
	<form action="./cookie_del.cgi" method="post">
	<input type="hidden" name="del_cookie" value="on">
	<input type="submit" value="����ID���폜"> $msg
	</form>
</body>
</html>
EOM
	exit;
}