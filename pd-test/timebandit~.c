//
//  timebandit~.c
//  timebandit~
//
//  Created by Jordan Kusel on 1/14/17.
//  Copyright © 2017 jordankusel. All rights reserved.
//

#include "m_pd.h"
#include <math.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <unistd.h>
#include <netdb.h>
#include <stdlib.h>

#define MAX_BEATS 1024
#define MAX_INSTS 8

#define DEFAULT_IP          "127.0.0.1"
#define IP_SIZE             16
#define DEFAULT_PORT        8500
#define SOCKET_SIZE         1024
#define PING_SAMPLE_TIME    44100             // how frequently to ping the python server
#define INST_NAME_SIZE      32

static t_class *timebandit_class;

struct _inst {
    int beats[MAX_BEATS];
    short beat_index;
    short beat_len;
    
    long sample_phase;
    float sample_inc;
    long sample_len;
    
    int phase;
    float scale;
    char *name;
    unsigned int name_bytes;
    
    int dead;
};

typedef struct _timebandit {
    t_object obj;
    t_float x_f;
    
    t_float *outs[MAX_INSTS];
    int out_bytes;
    
    t_outlet *out_metro[MAX_INSTS];
    int metro_bytes;
    
    int *arg;
    short arg_store;
    int arg_len;
    long sample_test;
    
    int sr;
    
    struct _inst insts[MAX_INSTS];
    
    int socket_desc;
    void *socket_clock;
    short port;
    char *ip;
    unsigned int ip_bytes;
    char remote[SOCKET_SIZE];
    struct sockaddr_in server;
    short connected;
    short ping_counter;
} t_timebandit;

void *timebandit_new(void);
void timebandit_dsp(t_timebandit *x, t_signal **sp); // does this need short *count?
void timebandit_onBangMsg(t_timebandit *x);
void timebandit_onLinkMsg(t_timebandit *x);//, t_symbol *msg, short argc, t_atom *argv);
void timebandit_onListMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv);
void timebandit_onPortMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv);
void timebandit_onIPMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv);
void timebandit_onRecvMsg(t_timebandit *x);
void timebandit_onLinkTestMsg(t_timebandit *x);
void timebandit_onHandshakeMsg(t_timebandit *x);

void check_socket(t_timebandit *x);

void parse_LinkMsg(t_timebandit *x);
void parse_Inst(t_timebandit *x, char *remote);
void parse_Beats(struct _inst *inst, char *remote);

int beat_increment(struct _inst *inst, int sr);

t_int *timebandit_perform(t_int *w);

void check_socket(t_timebandit *x) {
    post("did we make it?");
    timebandit_onHandshakeMsg(x);
    /*if (recv(x->socket_desc, x->remote, SOCKET_SIZE, 0) < 0) {
        post("[timebandit~ ]: read from socket %s:%d failed", DEFAULT_IP, DEFAULT_PORT);
    } else { //#########################
        post("%s", x->remote);
        //parse_LinkMsg(x);
    }*/
}

void parse_Inst(t_timebandit *x, char *remote) {
    char *token = remote;
    const char *inst_delim = ":";
    const char *name_delim = "~";
    char *lasts;
    token = strtok_r(token, inst_delim, &lasts);
    post("index: %s", token);
    struct _inst *inst;
    inst = &x->insts[atoi(token)];
    char *name = strtok_r(NULL, inst_delim, &lasts);
    char *name_lasts;
    name = strtok_r(name, name_delim, &name_lasts);
    post("name: %s", name);
    inst->name = name;
    token = strtok_r(NULL, name_delim, &name_lasts);
    parse_Beats(inst, token);
    inst->beat_index = inst->beat_len;
    beat_increment(inst, x->sr);
}

void parse_Beats(struct _inst *inst, char *remote) {
    char *token = remote;
    const char *beat_delim = ",";
    char *lasts;
    token = strtok_r(token, beat_delim, &lasts);
    short b = 0;
    inst->beat_len = 0;
    while(token) {
        post("beat: %s", token);
        inst->beats[b++] = atoi(token);
        inst->dead = 0;
        inst->beat_len++;
        token = strtok_r(NULL, beat_delim, &lasts);
    }
}

void parse_LinkMsg(t_timebandit *x) {
    char *remote = x->remote;
    const char *command_delim = ";";
    char *lasts;
    char *token;
    
    token = strtok_r(remote, command_delim, &lasts);
    while(token) { //loop each command
        post("command: %s", token);
        parse_Inst(x, token);
        token = strtok_r(NULL, command_delim, &lasts);
    }
}

int beat_increment(struct _inst *inst, int sr) {
    int dead = 0;
    if (inst->beat_index++ < inst->beat_len) {
        dead = 0;
    } else {
        inst->beat_index = 0;
        dead = 1;
    }
    inst->sample_len = trunc((float) (inst->beats[inst->beat_index] * sr) / 1000.0);
    inst->sample_phase = inst->sample_len;
    inst->dead = dead;
    return dead;
}

void timebandit_onBangMsg(t_timebandit *x) {
    /*short i;
    for (i = 0; i < x->arg_store; i++) {
     post("%d %d", i, x->arg[i]);
     }*/
    post("helloworld");
}

void timebandit_onLinkMsg(t_timebandit *x) {
    x->socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    if (x->socket_desc == -1) {
        post("[timebandit~ ]: error creating socket");
    }
    
    x->server.sin_addr.s_addr = inet_addr(x->ip);
    x->server.sin_family = AF_INET;
    x->server.sin_port = htons(x->port);
    
    if (connect(x->socket_desc, (struct sockaddr *) &x->server, sizeof(x->server)) < 0) {
        post("[timebandit~ ]: error connecting to remote server");
        x->connected = 1;
    } else {
        x->connected = 0;
    }
    /*if (recv(x->socket_desc, x->remote, SOCKET_SIZE, 0) < 0) {
        post("[timebandit~ ]: read from socket %s:%d failed", DEFAULT_IP, DEFAULT_PORT);
    }
    post("%s", x->remote);
    parse_LinkMsg(x);
    close(x->socket_desc);*/
}

void timebandit_onRecvMsg(t_timebandit *x) {
    if (recv(x->socket_desc, x->remote, SOCKET_SIZE, 0) < 0) {
        post("[timebandit~ ]: read from socket %s:%d failed", DEFAULT_IP, DEFAULT_PORT);
    } else {
        post("%s", x->remote);
        parse_LinkMsg(x);
    }
}

void timebandit_onPortMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv) {
    if(argc == 1) {
        x->port = (short) atom_getint(argv);
        post("[timebandit~ ]: port changed to %d", x->port);
    } else {
        error("[timebandit~ ]: specify port change with \"port <integer>\"");
    }
}

void timebandit_onIPMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv) {
    if(argc == 1) {
        atom_string(argv, x->ip, x->ip_bytes);
        post("[timebandit~ ]: IP changed to %s", x->ip);
    } else {
        error("[timebandit~ ]: specify port change with \"port <string>\"");
    }
}

void timebandit_onListMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv) {
    t_atom *list_msg = argv;
    short i;
    for (i = 0; i < argc; i++) {
        x->arg[i] = (int) atom_getfloat(list_msg + i);
    }
    /*short the_post = 1;
     for (int i = 0; i < argc; i++) {
     the_post = (short) atom_getfloat(argv + i);
     post("%d", the_post);
     }*/
    x->arg_store = argc;
    post("phew");
}

void timebandit_onLinkTestMsg(t_timebandit *x) {
    x->socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    if (x->socket_desc == -1) {
        post("[timebandit~ ]: error creating socket");
    }
    
    x->server.sin_addr.s_addr = inet_addr(x->ip);
    x->server.sin_family = AF_INET;
    x->server.sin_port = htons(x->port);
    
    if (connect(x->socket_desc, (struct sockaddr *) &x->server, sizeof(x->server)) < 0) {
        post("[timebandit~ ]: error connecting to remote server");
        x->connected = 0;
    } else {
        x->connected = 1;
        /*if (recv(x->socket_desc, x->remote, SOCKET_SIZE, 0) < 0) {
            post("[timebandit~ ]: read from socket %s:%d failed", DEFAULT_IP, DEFAULT_PORT);
        } else {
            post("%s", x->remote);
        }*/
    }
}

void timebandit_onHandshakeMsg(t_timebandit *x) {
    if (x->connected) {
        if(send(x->socket_desc, "handshake", strlen("handshake"), 0) < 0) {
            post("send failed");
            x->connected = 0;
        } else if(recv(x->socket_desc, x->remote, SOCKET_SIZE, 0) < 0) {
            post("recv failed");
            x->connected = 0;
        } else {
            post("%s", x->remote);
        }
    }
}

void timebandit_onInstMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv) {
    t_atom *inst_msg = argv;
    if (argc > 2) {
        short i;
        int inst_index = (int) atom_getfloat(inst_msg);
        post("%d inst", inst_index);
        struct _inst *inst = &x->insts[inst_index]; // the first argument is the instrument index
        
        atom_string(inst_msg + 1, inst->name, inst->name_bytes);
        
        for (i = 2; i < argc; i++) {
            inst->beats[i - 2] = (int) atom_getfloat(inst_msg + i);
            inst->dead = 0;
            inst->beat_len++;
            post("%d", x->insts[inst_index].beats[i - 2]);
        }
        inst->beat_index = inst->beat_len;
        beat_increment(inst, x->sr);
        post("%d, %d, %d", inst->beat_index, inst->sample_phase, inst->sample_len);
    }
}

void timebandit_onSchemeMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv) {
    t_atom *scheme_msg = argv;
    short i;
    for (i = 0; i < argc; i++) {
        post("%d", (int) atom_getfloat(scheme_msg+i));
    }
}

void timebandit_free(t_timebandit *x) {
    if (x->connected) {
        close(x->socket_desc);
    }
    freebytes(x->arg, x->arg_len);
    freebytes(x->insts, sizeof(struct _inst) * MAX_INSTS);
    freebytes(x->ip, IP_SIZE);
    short i;
    for (i = 0; i < MAX_INSTS; i++) {
        outlet_free(x->out_metro[i]);
    }
    clock_free(x->socket_clock);
}

void timebandit_tilde_setup(void) {
    timebandit_class = class_new(gensym("timebandit~"),
                                 (t_newmethod)timebandit_new,
                                 (t_method)timebandit_free,
                                 sizeof(t_timebandit),
                                 0, 0);
    CLASS_MAINSIGNALIN(timebandit_class, t_timebandit, x_f);
    class_addmethod(timebandit_class, (t_method)timebandit_dsp, gensym("dsp"), 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onBangMsg, gensym("bang"), 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onLinkMsg, gensym("link"), 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onListMsg, gensym("list"), A_GIMME, 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onInstMsg, gensym("inst"), A_GIMME, 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onPortMsg, gensym("port"), A_GIMME, 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onIPMsg, gensym("ip"), A_GIMME, 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onRecvMsg, gensym("recv"), 0);
    
    class_addmethod(timebandit_class, (t_method)timebandit_onSchemeMsg, gensym("scheme"), A_GIMME, 0);
    
    class_addmethod(timebandit_class, (t_method) timebandit_onHandshakeMsg, gensym("handshake"), 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onLinkTestMsg, gensym("listtest"), 0);
    
    post("[timebandit~ ]: http://github.com/ultraturtle0/timebandit.git");
}

void *timebandit_new(void) {
    t_timebandit *x = (t_timebandit *) pd_new(timebandit_class);
    
    x->arg_len = MAX_BEATS * sizeof(int);
    x->arg = (int *) getbytes(x->arg_len);
    
    //short p;
    /*x->out_bytes = MAX_INSTS * sizeof(t_float *);
    x->outs = (t_float *) getbytes(x->out_bytes);*/
    
    x->port = DEFAULT_PORT;
    x->ip = getbytes(IP_SIZE);
    x->ping_counter = PING_SAMPLE_TIME;
    x->connected = 0;
    x->sample_test = 44100;
    
    x->sr = 44100;
    
    strcpy(x->ip, DEFAULT_IP);
    
    //x->insts = (struct _inst *) getbytes(sizeof(struct _inst) * MAX_INSTS);
    x->socket_clock = clock_new(x, (t_method) check_socket);
    
    inlet_new(&x->obj, &x->obj.ob_pd, gensym("signal"), gensym("signal"));
    struct _inst *inst;
    short i;
    for(i = 0; i < MAX_INSTS; i++) {
        inst = &x->insts[i];
        inst->name = getbytes(INST_NAME_SIZE);
        inst->beat_index = 0;
        inst->beat_len = 0;
        inst->phase = 0;
        inst->sample_phase = 44100;
        inst->sample_len = inst->sample_phase;
        inst->dead = 1;
        strcpy(inst->name, "NULL");
        post("inst %s", inst->name);
        outlet_new(&x->obj, gensym("signal"));
    }
    for(i = 0; i < MAX_INSTS; i++) {
        x->out_metro[i] = outlet_new(&x->obj, &s_bang);
    }
    return x;
}

void timebandit_dsp(t_timebandit *x, t_signal **sp) {
    if (x->sr != sp[0]->s_sr && sp[0]->s_sr) { // if sampling rate changes
        x->sr = (int) sp[0]->s_sr;
    }
    dsp_add(timebandit_perform, 12, x, sp[0]->s_vec, sp[1]->s_vec, sp[2]->s_vec, sp[3]->s_vec, sp[4]->s_vec, sp[5]->s_vec, sp[6]->s_vec, sp[7]->s_vec, sp[8]->s_vec, sp[9]->s_vec, sp[0]->s_n); // pg 29
}

t_int *timebandit_perform(t_int *w) {
    t_timebandit *x = (t_timebandit *) (w[1]);
    //t_float *in = (t_float *) (w[2]);
    //t_float *in2 = (t_float *) (w[3]);
    
    short o;
    for (o = 0; o < MAX_INSTS; o++) {
        x->outs[o] = (t_float *) (w[o + 4]);
    }
    //t_float *testout = (t_float *) (w[3]);
    //x->outs[0] = (t_float *) (w[4]);
    t_int n = w[12];
    
    t_float sig = 0.0;
    //float pre_sig = 0.0;
    
    struct _inst *inst;
    long sample_phase;
    long sample_len;
    short the_bang = 0;
    short ping_counter = x->ping_counter;
    //char last_remote[SOCKET_SIZE];
    //strcpy(last_remote, x->remote);
    
    while(n--) {
        //while (! inst->dead) {
        if (! ping_counter-- && x->connected) {
            clock_delay(x->socket_clock, 0);
            ping_counter = PING_SAMPLE_TIME;
        }
        if (x->connected) {
            
        }
        for (o = 0; o < MAX_INSTS; o++) {
            inst = &x->insts[o];
            sample_phase = inst->sample_phase;
            sample_len = inst->sample_len;
            if (! sample_phase--) { // descending phasor samples
                beat_increment(inst, x->sr);
                sample_len = inst->sample_len;
                sample_phase = inst->sample_phase;
                sig = (t_float) 0.0;
                the_bang = 1;
            } else {
                sig = (t_float) ((float) sample_phase / (float) sample_len);
            }

            *x->outs[o]++ = sig;
            if (the_bang) {
                outlet_bang(x->out_metro[o]);
                //clock_delay(bang_clock(x->out_metro[o]), 0);
                the_bang = 0;
            }
            inst->sample_phase = sample_phase;
            inst->sample_len = sample_len;
        }
    }
    x->ping_counter = ping_counter;
    return w + 13;
    //post("%d", sig);
}
