
#include <stdio.h>
#include <stddef.h>
#include <stdarg.h>
#include <errno.h>
#include <sys/types.h>   /* XXX for ssize_t on some platforms */

/* this block of #ifs should be kept exactly identical between
   c/_cffi_backend.c, cffi/vengine_cpy.py, cffi/vengine_gen.py */
#if defined(_MSC_VER)
# include <malloc.h>   /* for alloca() */
# if _MSC_VER < 1600   /* MSVC < 2010 */
   typedef __int8 int8_t;
   typedef __int16 int16_t;
   typedef __int32 int32_t;
   typedef __int64 int64_t;
   typedef unsigned __int8 uint8_t;
   typedef unsigned __int16 uint16_t;
   typedef unsigned __int32 uint32_t;
   typedef unsigned __int64 uint64_t;
# else
#  include <stdint.h>
# endif
# if _MSC_VER < 1800   /* MSVC < 2013 */
   typedef unsigned char _Bool;
# endif
#else
# include <stdint.h>
# if (defined (__SVR4) && defined (__sun)) || defined(_AIX)
#  include <alloca.h>
# endif
#endif

#include <stdio.h>
#include <sys/un.h>
#include <string.h>

#include <zmq.h>
#include <zmq_utils.h>
#include "zmq_compat.h"

int get_ipc_path_max_len(void) {
    struct sockaddr_un *dummy;
    return sizeof(dummy->sun_path) - 1;
}

static void _cffi_check__zmq_msg_t(zmq_msg_t *p)
{
  /* only to generate compile-time warnings or errors */
}
intptr_t _cffi_layout__zmq_msg_t(intptr_t i)
{
  struct _cffi_aligncheck { char x; zmq_msg_t y; };
  static intptr_t nums[] = {
    sizeof(zmq_msg_t),
    offsetof(struct _cffi_aligncheck, y),
    -1
  };
  return nums[i];
  /* the next line is not executed, but compiled */
  _cffi_check__zmq_msg_t(0);
}

static void _cffi_check__zmq_pollitem_t(zmq_pollitem_t *p)
{
  /* only to generate compile-time warnings or errors */
  { void * *tmp = &p->socket; (void)tmp; }
  (void)((p->fd) << 1);
  (void)((p->events) << 1);
  (void)((p->revents) << 1);
}
intptr_t _cffi_layout__zmq_pollitem_t(intptr_t i)
{
  struct _cffi_aligncheck { char x; zmq_pollitem_t y; };
  static intptr_t nums[] = {
    sizeof(zmq_pollitem_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(zmq_pollitem_t, socket),
    sizeof(((zmq_pollitem_t *)0)->socket),
    offsetof(zmq_pollitem_t, fd),
    sizeof(((zmq_pollitem_t *)0)->fd),
    offsetof(zmq_pollitem_t, events),
    sizeof(((zmq_pollitem_t *)0)->events),
    offsetof(zmq_pollitem_t, revents),
    sizeof(((zmq_pollitem_t *)0)->revents),
    -1
  };
  return nums[i];
  /* the next line is not executed, but compiled */
  _cffi_check__zmq_pollitem_t(0);
}

int _cffi_f_get_ipc_path_max_len(void)
{
  return get_ipc_path_max_len();
}

void * _cffi_f_memcpy(void * x0, void const * x1, size_t x2)
{
  return memcpy(x0, x1, x2);
}

int _cffi_f_zmq_bind(void * x0, char const * x1)
{
  return zmq_bind(x0, x1);
}

int _cffi_f_zmq_close(void * x0)
{
  return zmq_close(x0);
}

int _cffi_f_zmq_connect(void * x0, char const * x1)
{
  return zmq_connect(x0, x1);
}

int _cffi_f_zmq_ctx_destroy(void * x0)
{
  return zmq_ctx_destroy(x0);
}

int _cffi_f_zmq_ctx_get(void * x0, int x1)
{
  return zmq_ctx_get(x0, x1);
}

void * _cffi_f_zmq_ctx_new(void)
{
  return zmq_ctx_new();
}

int _cffi_f_zmq_ctx_set(void * x0, int x1, int x2)
{
  return zmq_ctx_set(x0, x1, x2);
}

int _cffi_f_zmq_curve_keypair(char * x0, char * x1)
{
  return zmq_curve_keypair(x0, x1);
}

int _cffi_f_zmq_device(int x0, void * x1, void * x2)
{
  return zmq_device(x0, x1, x2);
}

int _cffi_f_zmq_disconnect(void * x0, char const * x1)
{
  return zmq_disconnect(x0, x1);
}

int _cffi_f_zmq_errno(void)
{
  return zmq_errno();
}

int _cffi_f_zmq_getsockopt(void * x0, int x1, void * x2, size_t * x3)
{
  return zmq_getsockopt(x0, x1, x2, x3);
}

int _cffi_f_zmq_has(char const * x0)
{
  return zmq_has(x0);
}

int _cffi_f_zmq_msg_close(zmq_msg_t * x0)
{
  return zmq_msg_close(x0);
}

void * _cffi_f_zmq_msg_data(zmq_msg_t * x0)
{
  return zmq_msg_data(x0);
}

int _cffi_f_zmq_msg_init(zmq_msg_t * x0)
{
  return zmq_msg_init(x0);
}

int _cffi_f_zmq_msg_init_data(zmq_msg_t * x0, void * x1, size_t x2, zmq_free_fn * x3, void * x4)
{
  return zmq_msg_init_data(x0, x1, x2, x3, x4);
}

int _cffi_f_zmq_msg_init_size(zmq_msg_t * x0, size_t x1)
{
  return zmq_msg_init_size(x0, x1);
}

int _cffi_f_zmq_msg_recv(zmq_msg_t * x0, void * x1, int x2)
{
  return zmq_msg_recv(x0, x1, x2);
}

int _cffi_f_zmq_msg_send(zmq_msg_t * x0, void * x1, int x2)
{
  return zmq_msg_send(x0, x1, x2);
}

size_t _cffi_f_zmq_msg_size(zmq_msg_t * x0)
{
  return zmq_msg_size(x0);
}

int _cffi_f_zmq_poll(zmq_pollitem_t * x0, int x1, long x2)
{
  return zmq_poll(x0, x1, x2);
}

int _cffi_f_zmq_proxy(void * x0, void * x1, void * x2)
{
  return zmq_proxy(x0, x1, x2);
}

int _cffi_f_zmq_setsockopt(void * x0, int x1, void const * x2, size_t x3)
{
  return zmq_setsockopt(x0, x1, x2, x3);
}

void _cffi_f_zmq_sleep(int x0)
{
  zmq_sleep(x0);
}

void * _cffi_f_zmq_socket(void * x0, int x1)
{
  return zmq_socket(x0, x1);
}

int _cffi_f_zmq_socket_monitor(void * x0, char const * x1, int x2)
{
  return zmq_socket_monitor(x0, x1, x2);
}

void * _cffi_f_zmq_stopwatch_start(void)
{
  return zmq_stopwatch_start();
}

unsigned long _cffi_f_zmq_stopwatch_stop(void * x0)
{
  return zmq_stopwatch_stop(x0);
}

char const * _cffi_f_zmq_strerror(int x0)
{
  return zmq_strerror(x0);
}

int _cffi_f_zmq_unbind(void * x0, char const * x1)
{
  return zmq_unbind(x0, x1);
}

void _cffi_f_zmq_version(int * x0, int * x1, int * x2)
{
  zmq_version(x0, x1, x2);
}

int _cffi_const_EADDRINUSE(long long *out_value)
{
  *out_value = (long long)(EADDRINUSE);
  return (EADDRINUSE) <= 0;
}

int _cffi_const_EADDRNOTAVAIL(long long *out_value)
{
  *out_value = (long long)(EADDRNOTAVAIL);
  return (EADDRNOTAVAIL) <= 0;
}

int _cffi_const_EAFNOSUPPORT(long long *out_value)
{
  *out_value = (long long)(EAFNOSUPPORT);
  return (EAFNOSUPPORT) <= 0;
}

int _cffi_const_EAGAIN(long long *out_value)
{
  *out_value = (long long)(EAGAIN);
  return (EAGAIN) <= 0;
}

int _cffi_const_ECONNABORTED(long long *out_value)
{
  *out_value = (long long)(ECONNABORTED);
  return (ECONNABORTED) <= 0;
}

int _cffi_const_ECONNREFUSED(long long *out_value)
{
  *out_value = (long long)(ECONNREFUSED);
  return (ECONNREFUSED) <= 0;
}

int _cffi_const_ECONNRESET(long long *out_value)
{
  *out_value = (long long)(ECONNRESET);
  return (ECONNRESET) <= 0;
}

int _cffi_const_EFAULT(long long *out_value)
{
  *out_value = (long long)(EFAULT);
  return (EFAULT) <= 0;
}

int _cffi_const_EFSM(long long *out_value)
{
  *out_value = (long long)(EFSM);
  return (EFSM) <= 0;
}

int _cffi_const_EHOSTUNREACH(long long *out_value)
{
  *out_value = (long long)(EHOSTUNREACH);
  return (EHOSTUNREACH) <= 0;
}

int _cffi_const_EINPROGRESS(long long *out_value)
{
  *out_value = (long long)(EINPROGRESS);
  return (EINPROGRESS) <= 0;
}

int _cffi_const_EINVAL(long long *out_value)
{
  *out_value = (long long)(EINVAL);
  return (EINVAL) <= 0;
}

int _cffi_const_EMSGSIZE(long long *out_value)
{
  *out_value = (long long)(EMSGSIZE);
  return (EMSGSIZE) <= 0;
}

int _cffi_const_EMTHREAD(long long *out_value)
{
  *out_value = (long long)(EMTHREAD);
  return (EMTHREAD) <= 0;
}

int _cffi_const_ENETDOWN(long long *out_value)
{
  *out_value = (long long)(ENETDOWN);
  return (ENETDOWN) <= 0;
}

int _cffi_const_ENETRESET(long long *out_value)
{
  *out_value = (long long)(ENETRESET);
  return (ENETRESET) <= 0;
}

int _cffi_const_ENETUNREACH(long long *out_value)
{
  *out_value = (long long)(ENETUNREACH);
  return (ENETUNREACH) <= 0;
}

int _cffi_const_ENOBUFS(long long *out_value)
{
  *out_value = (long long)(ENOBUFS);
  return (ENOBUFS) <= 0;
}

int _cffi_const_ENOCOMPATPROTO(long long *out_value)
{
  *out_value = (long long)(ENOCOMPATPROTO);
  return (ENOCOMPATPROTO) <= 0;
}

int _cffi_const_ENODEV(long long *out_value)
{
  *out_value = (long long)(ENODEV);
  return (ENODEV) <= 0;
}

int _cffi_const_ENOMEM(long long *out_value)
{
  *out_value = (long long)(ENOMEM);
  return (ENOMEM) <= 0;
}

int _cffi_const_ENOTCONN(long long *out_value)
{
  *out_value = (long long)(ENOTCONN);
  return (ENOTCONN) <= 0;
}

int _cffi_const_ENOTSOCK(long long *out_value)
{
  *out_value = (long long)(ENOTSOCK);
  return (ENOTSOCK) <= 0;
}

int _cffi_const_ENOTSUP(long long *out_value)
{
  *out_value = (long long)(ENOTSUP);
  return (ENOTSUP) <= 0;
}

int _cffi_const_EPROTONOSUPPORT(long long *out_value)
{
  *out_value = (long long)(EPROTONOSUPPORT);
  return (EPROTONOSUPPORT) <= 0;
}

int _cffi_const_ETERM(long long *out_value)
{
  *out_value = (long long)(ETERM);
  return (ETERM) <= 0;
}

int _cffi_const_ETIMEDOUT(long long *out_value)
{
  *out_value = (long long)(ETIMEDOUT);
  return (ETIMEDOUT) <= 0;
}

int _cffi_const_ZMQ_AFFINITY(long long *out_value)
{
  *out_value = (long long)(ZMQ_AFFINITY);
  return (ZMQ_AFFINITY) <= 0;
}

int _cffi_const_ZMQ_BACKLOG(long long *out_value)
{
  *out_value = (long long)(ZMQ_BACKLOG);
  return (ZMQ_BACKLOG) <= 0;
}

int _cffi_const_ZMQ_CONFLATE(long long *out_value)
{
  *out_value = (long long)(ZMQ_CONFLATE);
  return (ZMQ_CONFLATE) <= 0;
}

int _cffi_const_ZMQ_CONNECT_RID(long long *out_value)
{
  *out_value = (long long)(ZMQ_CONNECT_RID);
  return (ZMQ_CONNECT_RID) <= 0;
}

int _cffi_const_ZMQ_CURVE(long long *out_value)
{
  *out_value = (long long)(ZMQ_CURVE);
  return (ZMQ_CURVE) <= 0;
}

int _cffi_const_ZMQ_CURVE_PUBLICKEY(long long *out_value)
{
  *out_value = (long long)(ZMQ_CURVE_PUBLICKEY);
  return (ZMQ_CURVE_PUBLICKEY) <= 0;
}

int _cffi_const_ZMQ_CURVE_SECRETKEY(long long *out_value)
{
  *out_value = (long long)(ZMQ_CURVE_SECRETKEY);
  return (ZMQ_CURVE_SECRETKEY) <= 0;
}

int _cffi_const_ZMQ_CURVE_SERVER(long long *out_value)
{
  *out_value = (long long)(ZMQ_CURVE_SERVER);
  return (ZMQ_CURVE_SERVER) <= 0;
}

int _cffi_const_ZMQ_CURVE_SERVERKEY(long long *out_value)
{
  *out_value = (long long)(ZMQ_CURVE_SERVERKEY);
  return (ZMQ_CURVE_SERVERKEY) <= 0;
}

int _cffi_const_ZMQ_DEALER(long long *out_value)
{
  *out_value = (long long)(ZMQ_DEALER);
  return (ZMQ_DEALER) <= 0;
}

int _cffi_const_ZMQ_DELAY_ATTACH_ON_CONNECT(long long *out_value)
{
  *out_value = (long long)(ZMQ_DELAY_ATTACH_ON_CONNECT);
  return (ZMQ_DELAY_ATTACH_ON_CONNECT) <= 0;
}

int _cffi_const_ZMQ_DONTWAIT(long long *out_value)
{
  *out_value = (long long)(ZMQ_DONTWAIT);
  return (ZMQ_DONTWAIT) <= 0;
}

int _cffi_const_ZMQ_DOWNSTREAM(long long *out_value)
{
  *out_value = (long long)(ZMQ_DOWNSTREAM);
  return (ZMQ_DOWNSTREAM) <= 0;
}

int _cffi_const_ZMQ_EVENTS(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENTS);
  return (ZMQ_EVENTS) <= 0;
}

int _cffi_const_ZMQ_EVENT_ACCEPTED(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_ACCEPTED);
  return (ZMQ_EVENT_ACCEPTED) <= 0;
}

int _cffi_const_ZMQ_EVENT_ACCEPT_FAILED(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_ACCEPT_FAILED);
  return (ZMQ_EVENT_ACCEPT_FAILED) <= 0;
}

int _cffi_const_ZMQ_EVENT_ALL(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_ALL);
  return (ZMQ_EVENT_ALL) <= 0;
}

int _cffi_const_ZMQ_EVENT_BIND_FAILED(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_BIND_FAILED);
  return (ZMQ_EVENT_BIND_FAILED) <= 0;
}

int _cffi_const_ZMQ_EVENT_CLOSED(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_CLOSED);
  return (ZMQ_EVENT_CLOSED) <= 0;
}

int _cffi_const_ZMQ_EVENT_CLOSE_FAILED(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_CLOSE_FAILED);
  return (ZMQ_EVENT_CLOSE_FAILED) <= 0;
}

int _cffi_const_ZMQ_EVENT_CONNECTED(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_CONNECTED);
  return (ZMQ_EVENT_CONNECTED) <= 0;
}

int _cffi_const_ZMQ_EVENT_CONNECT_DELAYED(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_CONNECT_DELAYED);
  return (ZMQ_EVENT_CONNECT_DELAYED) <= 0;
}

int _cffi_const_ZMQ_EVENT_CONNECT_RETRIED(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_CONNECT_RETRIED);
  return (ZMQ_EVENT_CONNECT_RETRIED) <= 0;
}

int _cffi_const_ZMQ_EVENT_DISCONNECTED(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_DISCONNECTED);
  return (ZMQ_EVENT_DISCONNECTED) <= 0;
}

int _cffi_const_ZMQ_EVENT_LISTENING(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_LISTENING);
  return (ZMQ_EVENT_LISTENING) <= 0;
}

int _cffi_const_ZMQ_EVENT_MONITOR_STOPPED(long long *out_value)
{
  *out_value = (long long)(ZMQ_EVENT_MONITOR_STOPPED);
  return (ZMQ_EVENT_MONITOR_STOPPED) <= 0;
}

int _cffi_const_ZMQ_FAIL_UNROUTABLE(long long *out_value)
{
  *out_value = (long long)(ZMQ_FAIL_UNROUTABLE);
  return (ZMQ_FAIL_UNROUTABLE) <= 0;
}

int _cffi_const_ZMQ_FD(long long *out_value)
{
  *out_value = (long long)(ZMQ_FD);
  return (ZMQ_FD) <= 0;
}

int _cffi_const_ZMQ_FORWARDER(long long *out_value)
{
  *out_value = (long long)(ZMQ_FORWARDER);
  return (ZMQ_FORWARDER) <= 0;
}

int _cffi_const_ZMQ_GSSAPI(long long *out_value)
{
  *out_value = (long long)(ZMQ_GSSAPI);
  return (ZMQ_GSSAPI) <= 0;
}

int _cffi_const_ZMQ_GSSAPI_PLAINTEXT(long long *out_value)
{
  *out_value = (long long)(ZMQ_GSSAPI_PLAINTEXT);
  return (ZMQ_GSSAPI_PLAINTEXT) <= 0;
}

int _cffi_const_ZMQ_GSSAPI_PRINCIPAL(long long *out_value)
{
  *out_value = (long long)(ZMQ_GSSAPI_PRINCIPAL);
  return (ZMQ_GSSAPI_PRINCIPAL) <= 0;
}

int _cffi_const_ZMQ_GSSAPI_SERVER(long long *out_value)
{
  *out_value = (long long)(ZMQ_GSSAPI_SERVER);
  return (ZMQ_GSSAPI_SERVER) <= 0;
}

int _cffi_const_ZMQ_GSSAPI_SERVICE_PRINCIPAL(long long *out_value)
{
  *out_value = (long long)(ZMQ_GSSAPI_SERVICE_PRINCIPAL);
  return (ZMQ_GSSAPI_SERVICE_PRINCIPAL) <= 0;
}

int _cffi_const_ZMQ_HANDSHAKE_IVL(long long *out_value)
{
  *out_value = (long long)(ZMQ_HANDSHAKE_IVL);
  return (ZMQ_HANDSHAKE_IVL) <= 0;
}

int _cffi_const_ZMQ_HAUSNUMERO(long long *out_value)
{
  *out_value = (long long)(ZMQ_HAUSNUMERO);
  return (ZMQ_HAUSNUMERO) <= 0;
}

int _cffi_const_ZMQ_HWM(long long *out_value)
{
  *out_value = (long long)(ZMQ_HWM);
  return (ZMQ_HWM) <= 0;
}

int _cffi_const_ZMQ_IDENTITY(long long *out_value)
{
  *out_value = (long long)(ZMQ_IDENTITY);
  return (ZMQ_IDENTITY) <= 0;
}

int _cffi_const_ZMQ_IDENTITY_FD(long long *out_value)
{
  *out_value = (long long)(ZMQ_IDENTITY_FD);
  return (ZMQ_IDENTITY_FD) <= 0;
}

int _cffi_const_ZMQ_IMMEDIATE(long long *out_value)
{
  *out_value = (long long)(ZMQ_IMMEDIATE);
  return (ZMQ_IMMEDIATE) <= 0;
}

int _cffi_const_ZMQ_IO_THREADS(long long *out_value)
{
  *out_value = (long long)(ZMQ_IO_THREADS);
  return (ZMQ_IO_THREADS) <= 0;
}

int _cffi_const_ZMQ_IO_THREADS_DFLT(long long *out_value)
{
  *out_value = (long long)(ZMQ_IO_THREADS_DFLT);
  return (ZMQ_IO_THREADS_DFLT) <= 0;
}

int _cffi_const_ZMQ_IPC_FILTER_GID(long long *out_value)
{
  *out_value = (long long)(ZMQ_IPC_FILTER_GID);
  return (ZMQ_IPC_FILTER_GID) <= 0;
}

int _cffi_const_ZMQ_IPC_FILTER_PID(long long *out_value)
{
  *out_value = (long long)(ZMQ_IPC_FILTER_PID);
  return (ZMQ_IPC_FILTER_PID) <= 0;
}

int _cffi_const_ZMQ_IPC_FILTER_UID(long long *out_value)
{
  *out_value = (long long)(ZMQ_IPC_FILTER_UID);
  return (ZMQ_IPC_FILTER_UID) <= 0;
}

int _cffi_const_ZMQ_IPV4ONLY(long long *out_value)
{
  *out_value = (long long)(ZMQ_IPV4ONLY);
  return (ZMQ_IPV4ONLY) <= 0;
}

int _cffi_const_ZMQ_IPV6(long long *out_value)
{
  *out_value = (long long)(ZMQ_IPV6);
  return (ZMQ_IPV6) <= 0;
}

int _cffi_const_ZMQ_LAST_ENDPOINT(long long *out_value)
{
  *out_value = (long long)(ZMQ_LAST_ENDPOINT);
  return (ZMQ_LAST_ENDPOINT) <= 0;
}

int _cffi_const_ZMQ_LINGER(long long *out_value)
{
  *out_value = (long long)(ZMQ_LINGER);
  return (ZMQ_LINGER) <= 0;
}

int _cffi_const_ZMQ_MAXMSGSIZE(long long *out_value)
{
  *out_value = (long long)(ZMQ_MAXMSGSIZE);
  return (ZMQ_MAXMSGSIZE) <= 0;
}

int _cffi_const_ZMQ_MAX_SOCKETS(long long *out_value)
{
  *out_value = (long long)(ZMQ_MAX_SOCKETS);
  return (ZMQ_MAX_SOCKETS) <= 0;
}

int _cffi_const_ZMQ_MAX_SOCKETS_DFLT(long long *out_value)
{
  *out_value = (long long)(ZMQ_MAX_SOCKETS_DFLT);
  return (ZMQ_MAX_SOCKETS_DFLT) <= 0;
}

int _cffi_const_ZMQ_MCAST_LOOP(long long *out_value)
{
  *out_value = (long long)(ZMQ_MCAST_LOOP);
  return (ZMQ_MCAST_LOOP) <= 0;
}

int _cffi_const_ZMQ_MECHANISM(long long *out_value)
{
  *out_value = (long long)(ZMQ_MECHANISM);
  return (ZMQ_MECHANISM) <= 0;
}

int _cffi_const_ZMQ_MORE(long long *out_value)
{
  *out_value = (long long)(ZMQ_MORE);
  return (ZMQ_MORE) <= 0;
}

int _cffi_const_ZMQ_MULTICAST_HOPS(long long *out_value)
{
  *out_value = (long long)(ZMQ_MULTICAST_HOPS);
  return (ZMQ_MULTICAST_HOPS) <= 0;
}

int _cffi_const_ZMQ_NOBLOCK(long long *out_value)
{
  *out_value = (long long)(ZMQ_NOBLOCK);
  return (ZMQ_NOBLOCK) <= 0;
}

int _cffi_const_ZMQ_NULL(long long *out_value)
{
  *out_value = (long long)(ZMQ_NULL);
  return (ZMQ_NULL) <= 0;
}

int _cffi_const_ZMQ_PAIR(long long *out_value)
{
  *out_value = (long long)(ZMQ_PAIR);
  return (ZMQ_PAIR) <= 0;
}

int _cffi_const_ZMQ_PLAIN(long long *out_value)
{
  *out_value = (long long)(ZMQ_PLAIN);
  return (ZMQ_PLAIN) <= 0;
}

int _cffi_const_ZMQ_PLAIN_PASSWORD(long long *out_value)
{
  *out_value = (long long)(ZMQ_PLAIN_PASSWORD);
  return (ZMQ_PLAIN_PASSWORD) <= 0;
}

int _cffi_const_ZMQ_PLAIN_SERVER(long long *out_value)
{
  *out_value = (long long)(ZMQ_PLAIN_SERVER);
  return (ZMQ_PLAIN_SERVER) <= 0;
}

int _cffi_const_ZMQ_PLAIN_USERNAME(long long *out_value)
{
  *out_value = (long long)(ZMQ_PLAIN_USERNAME);
  return (ZMQ_PLAIN_USERNAME) <= 0;
}

int _cffi_const_ZMQ_POLLERR(long long *out_value)
{
  *out_value = (long long)(ZMQ_POLLERR);
  return (ZMQ_POLLERR) <= 0;
}

int _cffi_const_ZMQ_POLLIN(long long *out_value)
{
  *out_value = (long long)(ZMQ_POLLIN);
  return (ZMQ_POLLIN) <= 0;
}

int _cffi_const_ZMQ_POLLITEMS_DFLT(long long *out_value)
{
  *out_value = (long long)(ZMQ_POLLITEMS_DFLT);
  return (ZMQ_POLLITEMS_DFLT) <= 0;
}

int _cffi_const_ZMQ_POLLOUT(long long *out_value)
{
  *out_value = (long long)(ZMQ_POLLOUT);
  return (ZMQ_POLLOUT) <= 0;
}

int _cffi_const_ZMQ_PROBE_ROUTER(long long *out_value)
{
  *out_value = (long long)(ZMQ_PROBE_ROUTER);
  return (ZMQ_PROBE_ROUTER) <= 0;
}

int _cffi_const_ZMQ_PUB(long long *out_value)
{
  *out_value = (long long)(ZMQ_PUB);
  return (ZMQ_PUB) <= 0;
}

int _cffi_const_ZMQ_PULL(long long *out_value)
{
  *out_value = (long long)(ZMQ_PULL);
  return (ZMQ_PULL) <= 0;
}

int _cffi_const_ZMQ_PUSH(long long *out_value)
{
  *out_value = (long long)(ZMQ_PUSH);
  return (ZMQ_PUSH) <= 0;
}

int _cffi_const_ZMQ_QUEUE(long long *out_value)
{
  *out_value = (long long)(ZMQ_QUEUE);
  return (ZMQ_QUEUE) <= 0;
}

int _cffi_const_ZMQ_RATE(long long *out_value)
{
  *out_value = (long long)(ZMQ_RATE);
  return (ZMQ_RATE) <= 0;
}

int _cffi_const_ZMQ_RCVBUF(long long *out_value)
{
  *out_value = (long long)(ZMQ_RCVBUF);
  return (ZMQ_RCVBUF) <= 0;
}

int _cffi_const_ZMQ_RCVHWM(long long *out_value)
{
  *out_value = (long long)(ZMQ_RCVHWM);
  return (ZMQ_RCVHWM) <= 0;
}

int _cffi_const_ZMQ_RCVMORE(long long *out_value)
{
  *out_value = (long long)(ZMQ_RCVMORE);
  return (ZMQ_RCVMORE) <= 0;
}

int _cffi_const_ZMQ_RCVTIMEO(long long *out_value)
{
  *out_value = (long long)(ZMQ_RCVTIMEO);
  return (ZMQ_RCVTIMEO) <= 0;
}

int _cffi_const_ZMQ_RECONNECT_IVL(long long *out_value)
{
  *out_value = (long long)(ZMQ_RECONNECT_IVL);
  return (ZMQ_RECONNECT_IVL) <= 0;
}

int _cffi_const_ZMQ_RECONNECT_IVL_MAX(long long *out_value)
{
  *out_value = (long long)(ZMQ_RECONNECT_IVL_MAX);
  return (ZMQ_RECONNECT_IVL_MAX) <= 0;
}

int _cffi_const_ZMQ_RECOVERY_IVL(long long *out_value)
{
  *out_value = (long long)(ZMQ_RECOVERY_IVL);
  return (ZMQ_RECOVERY_IVL) <= 0;
}

int _cffi_const_ZMQ_RECOVERY_IVL_MSEC(long long *out_value)
{
  *out_value = (long long)(ZMQ_RECOVERY_IVL_MSEC);
  return (ZMQ_RECOVERY_IVL_MSEC) <= 0;
}

int _cffi_const_ZMQ_REP(long long *out_value)
{
  *out_value = (long long)(ZMQ_REP);
  return (ZMQ_REP) <= 0;
}

int _cffi_const_ZMQ_REQ(long long *out_value)
{
  *out_value = (long long)(ZMQ_REQ);
  return (ZMQ_REQ) <= 0;
}

int _cffi_const_ZMQ_REQ_CORRELATE(long long *out_value)
{
  *out_value = (long long)(ZMQ_REQ_CORRELATE);
  return (ZMQ_REQ_CORRELATE) <= 0;
}

int _cffi_const_ZMQ_REQ_RELAXED(long long *out_value)
{
  *out_value = (long long)(ZMQ_REQ_RELAXED);
  return (ZMQ_REQ_RELAXED) <= 0;
}

int _cffi_const_ZMQ_ROUTER(long long *out_value)
{
  *out_value = (long long)(ZMQ_ROUTER);
  return (ZMQ_ROUTER) <= 0;
}

int _cffi_const_ZMQ_ROUTER_BEHAVIOR(long long *out_value)
{
  *out_value = (long long)(ZMQ_ROUTER_BEHAVIOR);
  return (ZMQ_ROUTER_BEHAVIOR) <= 0;
}

int _cffi_const_ZMQ_ROUTER_HANDOVER(long long *out_value)
{
  *out_value = (long long)(ZMQ_ROUTER_HANDOVER);
  return (ZMQ_ROUTER_HANDOVER) <= 0;
}

int _cffi_const_ZMQ_ROUTER_MANDATORY(long long *out_value)
{
  *out_value = (long long)(ZMQ_ROUTER_MANDATORY);
  return (ZMQ_ROUTER_MANDATORY) <= 0;
}

int _cffi_const_ZMQ_ROUTER_RAW(long long *out_value)
{
  *out_value = (long long)(ZMQ_ROUTER_RAW);
  return (ZMQ_ROUTER_RAW) <= 0;
}

int _cffi_const_ZMQ_SHARED(long long *out_value)
{
  *out_value = (long long)(ZMQ_SHARED);
  return (ZMQ_SHARED) <= 0;
}

int _cffi_const_ZMQ_SNDBUF(long long *out_value)
{
  *out_value = (long long)(ZMQ_SNDBUF);
  return (ZMQ_SNDBUF) <= 0;
}

int _cffi_const_ZMQ_SNDHWM(long long *out_value)
{
  *out_value = (long long)(ZMQ_SNDHWM);
  return (ZMQ_SNDHWM) <= 0;
}

int _cffi_const_ZMQ_SNDMORE(long long *out_value)
{
  *out_value = (long long)(ZMQ_SNDMORE);
  return (ZMQ_SNDMORE) <= 0;
}

int _cffi_const_ZMQ_SNDTIMEO(long long *out_value)
{
  *out_value = (long long)(ZMQ_SNDTIMEO);
  return (ZMQ_SNDTIMEO) <= 0;
}

int _cffi_const_ZMQ_SOCKET_LIMIT(long long *out_value)
{
  *out_value = (long long)(ZMQ_SOCKET_LIMIT);
  return (ZMQ_SOCKET_LIMIT) <= 0;
}

int _cffi_const_ZMQ_SOCKS_PROXY(long long *out_value)
{
  *out_value = (long long)(ZMQ_SOCKS_PROXY);
  return (ZMQ_SOCKS_PROXY) <= 0;
}

int _cffi_const_ZMQ_SRCFD(long long *out_value)
{
  *out_value = (long long)(ZMQ_SRCFD);
  return (ZMQ_SRCFD) <= 0;
}

int _cffi_const_ZMQ_STREAM(long long *out_value)
{
  *out_value = (long long)(ZMQ_STREAM);
  return (ZMQ_STREAM) <= 0;
}

int _cffi_const_ZMQ_STREAMER(long long *out_value)
{
  *out_value = (long long)(ZMQ_STREAMER);
  return (ZMQ_STREAMER) <= 0;
}

int _cffi_const_ZMQ_SUB(long long *out_value)
{
  *out_value = (long long)(ZMQ_SUB);
  return (ZMQ_SUB) <= 0;
}

int _cffi_const_ZMQ_SUBSCRIBE(long long *out_value)
{
  *out_value = (long long)(ZMQ_SUBSCRIBE);
  return (ZMQ_SUBSCRIBE) <= 0;
}

int _cffi_const_ZMQ_SWAP(long long *out_value)
{
  *out_value = (long long)(ZMQ_SWAP);
  return (ZMQ_SWAP) <= 0;
}

int _cffi_const_ZMQ_TCP_ACCEPT_FILTER(long long *out_value)
{
  *out_value = (long long)(ZMQ_TCP_ACCEPT_FILTER);
  return (ZMQ_TCP_ACCEPT_FILTER) <= 0;
}

int _cffi_const_ZMQ_TCP_KEEPALIVE(long long *out_value)
{
  *out_value = (long long)(ZMQ_TCP_KEEPALIVE);
  return (ZMQ_TCP_KEEPALIVE) <= 0;
}

int _cffi_const_ZMQ_TCP_KEEPALIVE_CNT(long long *out_value)
{
  *out_value = (long long)(ZMQ_TCP_KEEPALIVE_CNT);
  return (ZMQ_TCP_KEEPALIVE_CNT) <= 0;
}

int _cffi_const_ZMQ_TCP_KEEPALIVE_IDLE(long long *out_value)
{
  *out_value = (long long)(ZMQ_TCP_KEEPALIVE_IDLE);
  return (ZMQ_TCP_KEEPALIVE_IDLE) <= 0;
}

int _cffi_const_ZMQ_TCP_KEEPALIVE_INTVL(long long *out_value)
{
  *out_value = (long long)(ZMQ_TCP_KEEPALIVE_INTVL);
  return (ZMQ_TCP_KEEPALIVE_INTVL) <= 0;
}

int _cffi_const_ZMQ_THREAD_PRIORITY(long long *out_value)
{
  *out_value = (long long)(ZMQ_THREAD_PRIORITY);
  return (ZMQ_THREAD_PRIORITY) <= 0;
}

int _cffi_const_ZMQ_THREAD_PRIORITY_DFLT(long long *out_value)
{
  *out_value = (long long)(ZMQ_THREAD_PRIORITY_DFLT);
  return (ZMQ_THREAD_PRIORITY_DFLT) <= 0;
}

int _cffi_const_ZMQ_THREAD_SCHED_POLICY(long long *out_value)
{
  *out_value = (long long)(ZMQ_THREAD_SCHED_POLICY);
  return (ZMQ_THREAD_SCHED_POLICY) <= 0;
}

int _cffi_const_ZMQ_THREAD_SCHED_POLICY_DFLT(long long *out_value)
{
  *out_value = (long long)(ZMQ_THREAD_SCHED_POLICY_DFLT);
  return (ZMQ_THREAD_SCHED_POLICY_DFLT) <= 0;
}

int _cffi_const_ZMQ_TOS(long long *out_value)
{
  *out_value = (long long)(ZMQ_TOS);
  return (ZMQ_TOS) <= 0;
}

int _cffi_const_ZMQ_TYPE(long long *out_value)
{
  *out_value = (long long)(ZMQ_TYPE);
  return (ZMQ_TYPE) <= 0;
}

int _cffi_const_ZMQ_UNSUBSCRIBE(long long *out_value)
{
  *out_value = (long long)(ZMQ_UNSUBSCRIBE);
  return (ZMQ_UNSUBSCRIBE) <= 0;
}

int _cffi_const_ZMQ_UPSTREAM(long long *out_value)
{
  *out_value = (long long)(ZMQ_UPSTREAM);
  return (ZMQ_UPSTREAM) <= 0;
}

int _cffi_const_ZMQ_VERSION(long long *out_value)
{
  *out_value = (long long)(ZMQ_VERSION);
  return (ZMQ_VERSION) <= 0;
}

int _cffi_const_ZMQ_VERSION_MAJOR(long long *out_value)
{
  *out_value = (long long)(ZMQ_VERSION_MAJOR);
  return (ZMQ_VERSION_MAJOR) <= 0;
}

int _cffi_const_ZMQ_VERSION_MINOR(long long *out_value)
{
  *out_value = (long long)(ZMQ_VERSION_MINOR);
  return (ZMQ_VERSION_MINOR) <= 0;
}

int _cffi_const_ZMQ_VERSION_PATCH(long long *out_value)
{
  *out_value = (long long)(ZMQ_VERSION_PATCH);
  return (ZMQ_VERSION_PATCH) <= 0;
}

int _cffi_const_ZMQ_XPUB(long long *out_value)
{
  *out_value = (long long)(ZMQ_XPUB);
  return (ZMQ_XPUB) <= 0;
}

int _cffi_const_ZMQ_XPUB_NODROP(long long *out_value)
{
  *out_value = (long long)(ZMQ_XPUB_NODROP);
  return (ZMQ_XPUB_NODROP) <= 0;
}

int _cffi_const_ZMQ_XPUB_VERBOSE(long long *out_value)
{
  *out_value = (long long)(ZMQ_XPUB_VERBOSE);
  return (ZMQ_XPUB_VERBOSE) <= 0;
}

int _cffi_const_ZMQ_XREP(long long *out_value)
{
  *out_value = (long long)(ZMQ_XREP);
  return (ZMQ_XREP) <= 0;
}

int _cffi_const_ZMQ_XREQ(long long *out_value)
{
  *out_value = (long long)(ZMQ_XREQ);
  return (ZMQ_XREQ) <= 0;
}

int _cffi_const_ZMQ_XSUB(long long *out_value)
{
  *out_value = (long long)(ZMQ_XSUB);
  return (ZMQ_XSUB) <= 0;
}

int _cffi_const_ZMQ_ZAP_DOMAIN(long long *out_value)
{
  *out_value = (long long)(ZMQ_ZAP_DOMAIN);
  return (ZMQ_ZAP_DOMAIN) <= 0;
}

