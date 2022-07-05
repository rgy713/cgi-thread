#!/usr/bin/perl

BEGIN {
    # �O���t�@�C����荞��
    require './init.cgi';
}
use Encode;
use JSON::XS;
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use HistoryCookie;
use HistoryLog;

# �L���b�V�������Ȃ�HTTP�w�b�_�[���o��
print <<'EOM';
Pragma: no-cache
Cache-Control: private, no-store, no-cache, must-revalidate, proxy-revalidate
Expires: Thu, 01 Dec 1994 16:00:00 GMT
EOM

# ����ID���擾
my $chistory_id = do {
    my $instance = HistoryCookie->new();
    $instance->get_history_id();
};

# ����ID���擾�ł��Ȃ����́A403��Ԃ�
if (!defined($chistory_id)) {
    print "Status: 403 Forbidden\n\n";
    exit;
}

# HistoryLog�C���X�^���X��������
my $history_log = HistoryLog->new($chistory_id);

if ($ENV{REQUEST_METHOD} eq 'GET') {
    print "Content-type: application/json; charset=utf-8\n\n";
    my $ng_settings_hash_ref = $history_log->get_read_ng_settings();
    my $json = JSON::XS->new->utf8(1)->encode($ng_settings_hash_ref);
    print $json;
} elsif ($ENV{REQUEST_METHOD} eq 'POST') {
    # POST���ꂽ�l���擾
    my $read_data;
    read(STDIN, $read_data, $ENV{CONTENT_LENGTH});

    # �L�[/�l�y�A�ɕ������A���͑Ώۂ̃L�[���n�b�V���ɂ���
    my %post_data;
    foreach my $key_val_pair (split(/&/, $read_data)) {
        my ($key, $json_val) = split(/=/, $key_val_pair);
        if ($key eq 'NGID_LIST' || $key eq 'NGNAME_LIST') {
            # URL�G���R�[�h����Ă���̂ŁA�f�R�[�h
            $json_val =~ tr/+/ /;
            $json_val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;

            # JSON�p�[�X
            $json_val = Encode::decode('UTF-8', $json_val);
            my $json_parsed_value = JSON::XS->new->utf8(0)->decode($json_val);

            # ���͒l�`�F�b�N���A�n�b�V���ɒǉ�
            if ($key eq 'NGID_LIST' && ref($json_parsed_value) eq 'ARRAY') {
                $post_data{$key} = $json_parsed_value;
            } elsif ($key eq 'NGNAME_LIST' && ref($json_parsed_value) eq 'HASH') {
                # �n�b�V�����őz�肵�Ă�����̓f�[�^�݂̂Ƀt�B���^�����O
                my %save_data;
                foreach my $key_in_hash (keys(%{$json_parsed_value})) {
                    my $value = ${$json_parsed_value}{$key_in_hash};
                    if (($key_in_hash eq 'name' || $key_in_hash eq 'trip') && ref($value) eq 'ARRAY') {
                        $save_data{$key_in_hash} = $value;
                    }
                }
                $post_data{$key} = \%save_data;
            } else {
                # �s���ȓ��͂̂��߁A400��Ԃ�
                print "Status: 400 Bad Request\n\n";
                # HistoryLog�C���X�^���X�����
                $history_log->DESTROY();
                exit;
            }
        }
    }

    # �ۑ��ΏۃL�[��1�ȏ゠�邩�ǂ���
    if (scalar(keys(%post_data)) > 0) {
        # �L�[�ɑΉ�����T�u���[�`�����Ăяo���A�l��ۑ�����
        foreach my $key (keys(%post_data)) {
            if ($key eq 'NGID_LIST') {
                $history_log->set_ngid_settings($post_data{$key});
            } elsif ($key eq 'NGNAME_LIST') {
                $history_log->set_ngname_settings($post_data{$key});
            }
        }
        # ����I�������̂ŁA200��Ԃ�
        print "Status: 200 OK\n\n";
    } else {
        # �s���ȓ��͂̂��߁A400��Ԃ�
        print "Status: 400 Bad Request\n\n";
    }
} else {
    # GET/POST�ȊO��405��Ԃ�
    print "Status: 405 Method Not Allowed\n\n";
}

# HistoryLog�C���X�^���X�����
$history_log->DESTROY();