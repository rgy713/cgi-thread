#!/usr/bin/perl

BEGIN {
    # 外部ファイル取り込み
    require './init.cgi';
}
use Encode;
use JSON::XS;
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use HistoryCookie;
use HistoryLog;

# キャッシュさせないHTTPヘッダーを出力
print <<'EOM';
Pragma: no-cache
Cache-Control: private, no-store, no-cache, must-revalidate, proxy-revalidate
Expires: Thu, 01 Dec 1994 16:00:00 GMT
EOM

# 書込IDを取得
my $chistory_id = do {
    my $instance = HistoryCookie->new();
    $instance->get_history_id();
};

# 書込IDを取得できない時は、403を返す
if (!defined($chistory_id)) {
    print "Status: 403 Forbidden\n\n";
    exit;
}

# HistoryLogインスタンスを初期化
my $history_log = HistoryLog->new($chistory_id);

if ($ENV{REQUEST_METHOD} eq 'GET') {
    print "Content-type: application/json; charset=utf-8\n\n";
    my $ng_settings_hash_ref = $history_log->get_read_ng_settings();
    my $json = JSON::XS->new->utf8(1)->encode($ng_settings_hash_ref);
    print $json;
} elsif ($ENV{REQUEST_METHOD} eq 'POST') {
    # POSTされた値を取得
    my $read_data;
    read(STDIN, $read_data, $ENV{CONTENT_LENGTH});

    # キー/値ペアに分割し、入力対象のキーをハッシュにする
    my %post_data;
    foreach my $key_val_pair (split(/&/, $read_data)) {
        my ($key, $json_val) = split(/=/, $key_val_pair);
        if ($key eq 'NGID_LIST' || $key eq 'NGNAME_LIST') {
            # URLエンコードされているので、デコード
            $json_val =~ tr/+/ /;
            $json_val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;

            # JSONパース
            $json_val = Encode::decode('UTF-8', $json_val);
            my $json_parsed_value = JSON::XS->new->utf8(0)->decode($json_val);

            # 入力値チェックし、ハッシュに追加
            if ($key eq 'NGID_LIST' && ref($json_parsed_value) eq 'ARRAY') {
                $post_data{$key} = $json_parsed_value;
            } elsif ($key eq 'NGNAME_LIST' && ref($json_parsed_value) eq 'HASH') {
                # ハッシュ内で想定している入力データのみにフィルタリング
                my %save_data;
                foreach my $key_in_hash (keys(%{$json_parsed_value})) {
                    my $value = ${$json_parsed_value}{$key_in_hash};
                    if (($key_in_hash eq 'name' || $key_in_hash eq 'trip') && ref($value) eq 'ARRAY') {
                        $save_data{$key_in_hash} = $value;
                    }
                }
                $post_data{$key} = \%save_data;
            } else {
                # 不正な入力のため、400を返す
                print "Status: 400 Bad Request\n\n";
                # HistoryLogインスタンスを解放
                $history_log->DESTROY();
                exit;
            }
        }
    }

    # 保存対象キーが1つ以上あるかどうか
    if (scalar(keys(%post_data)) > 0) {
        # キーに対応するサブルーチンを呼び出し、値を保存する
        foreach my $key (keys(%post_data)) {
            if ($key eq 'NGID_LIST') {
                $history_log->set_ngid_settings($post_data{$key});
            } elsif ($key eq 'NGNAME_LIST') {
                $history_log->set_ngname_settings($post_data{$key});
            }
        }
        # 正常終了したので、200を返す
        print "Status: 200 OK\n\n";
    } else {
        # 不正な入力のため、400を返す
        print "Status: 400 Bad Request\n\n";
    }
} else {
    # GET/POST以外は405を返す
    print "Status: 405 Method Not Allowed\n\n";
}

# HistoryLogインスタンスを解放
$history_log->DESTROY();