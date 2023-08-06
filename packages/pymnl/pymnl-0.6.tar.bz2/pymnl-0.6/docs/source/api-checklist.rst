libmnl to pymnl API checklist
=============================

This document compares the libmnl and pymnl API to make sure every
function in libmnl is accounted for.

socket
------

=============================   =============================
libmnl                          pymnl
=============================   =============================
mnl_socket_get_fd               Socket.get_sock
mnl_socket_get_portid           Socket.get_portid
mnl_socket_open                 Socket.__init__
mnl_socket_bind                 Socket.bind
mnl_socket_recvfrom             Socket.send
mnl_socket_sendto               Socket.recv
mnl_socket_close                Socket.close
mnl_socket_setsockopt           Socket.setsockopt
mnl_socket_getsockopt           Socket.getsockopt
=============================   =============================


nlmsg
-----

=============================   =============================
libmnl                          pymnl
=============================   =============================
mnl_nlmsg_size                  Message.__len__
mnl_nlmsg_get_payload           Message.get_payload
mnl_nlmsg_get_payload_len       Payload.__len__
mnl_nlmsg_get_payload_offset    not applicable
mnl_nlmsg_get_payload_tail      not applicable
mnl_nlmsg_put_header            not applicable
mnl_nlmsg_put_extra_header      Message.put_extra_header
mnl_nlmsg_next                  MessageList
mnl_nlmsg_ok                    Message.ok
mnl_nlmsg_seq_ok                Message.seq_ok
mnl_nlmsg_portid_ok             Message.portid_ok
mnl_nlmsg_fprintf_header        Message.printf_header
mnl_nlmsg_fprintf_payload       Payload.printf
mnl_nlmsg_fprintf               Message.printf
mnl_nlmsg_batch_start           not applicable
mnl_nlmsg_batch_stop            not applicable
mnl_nlmsg_batch_next            MessageList
mnl_nlmsg_batch_reset           MessageList
mnl_nlmsg_batch_size            MessageList.__len__
mnl_nlmsg_batch_head            MessageList
mnl_nlmsg_batch_current         MessageList
mnl_nlmsg_batch_is_empty        MessageList
=============================   =============================


attributes
----------

=============================   =============================
libmnl                          pymnl
=============================   =============================
mnl_attr_get_len                Attr.__len__
mnl_attr_get_payload            Attr.get_*
mnl_attr_get_payload_len        Attr.get_value_len
mnl_attr_get_type               Attr.get_type
mnl_attr_get_u8                 Attr.get_u8
mnl_attr_get_u16                Attr.get_u16
mnl_attr_get_u32                Attr.get_u32
mnl_attr_get_u64                Attr.get_u64
mnl_attr_get_str                Attr.get_str
                                Attr.get_str_stripped
mnl_attr_nest_end               not applicable
mnl_attr_nest_start             Attr.toggle_nested
mnl_attr_nest_start_check       not applicable
mnl_attr_nest_cancel            Attr.toggle_nested
mnl_attr_next                   not applicable
mnl_attr_ok                     not applicable
mnl_attr_parse                  AttrParser.parse
mnl_attr_parse_nested           AttrParser.parse_nested
mnl_attr_put                    Payload.add_attr
mnl_attr_put_u8                 Payload.add_attr(Attr.new_u8)
mnl_attr_put_u16                Payload.add_attr(Attr.new_u16)
mnl_attr_put_u32                Payload.add_attr(Attr.new_u32)
mnl_attr_put_u64                Payload.add_attr(Attr.new_u64)
mnl_attr_put_str                Payload.add_attr(Attr.new_str)
mnl_attr_put_strz               Payload.add_attr(Attr.new_strz)
mnl_attr_put_check              not applicable
mnl_attr_put_u8_check           not applicable
mnl_attr_put_u16_check          not applicable
mnl_attr_put_u32_check          not applicable
mnl_attr_put_u64_check          not applicable
mnl_attr_put_str_check          not applicable
mnl_attr_put_strz_check         not applicable
mnl_attr_type_valid             Attr.type_valid
__mnl_attr_validate             Attr.get_*
mnl_attr_validate               Attr.get_*
mnl_attr_validate2              Attr.get_*
=============================   =============================


callback
--------

=============================   =============================
libmnl                          pymnl
=============================   =============================
mnl_cb_run                      AttrParser
                                    MessageList
mnl_cb_run2                     subclass AttrParser
                                    MessageList
=============================   =============================
