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

#define DEFAULT_IP      "127.0.0.1"
#define IP_SIZE         16
#define DEFAULT_PORT    8500
#define SOCKET_SIZE     1024
#define INST_NAME_SIZE  32

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
    t_outlet *out_metro1;
    
    int *arg;
    short arg_store;
    int arg_len;
    long sample_test;
    
    int sr;
    
    struct _inst insts[MAX_INSTS];
    
    int socket_desc;
    short port;
    char *ip;
    unsigned int ip_bytes;
    char remote[SOCKET_SIZE];
    struct sockaddr_in server;
} t_timebandit;

void *timebandit_new(void);
void timebandit_dsp(t_timebandit *x, t_signal **sp); // does this need short *count?
void timebandit_onBangMsg(t_timebandit *x);
void timebandit_onLinkMsg(t_timebandit *x);//, t_symbol *msg, short argc, t_atom *argv);
void timebandit_onListMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv);
void timebandit_onPortMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv);
void timebandit_onIPMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv);

void parse_LinkMsg(t_timebandit *x);
void parse_Inst(t_timebandit *x, char *remote);
void parse_Beats(struct _inst *inst, char *remote);

int beat_increment(struct _inst *inst, int sr);

t_int *timebandit_perform(t_int *w);

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
    post("DO WE EVEN GET HERE");
    int dead = 0;
    if (inst->beat_index++ < inst->beat_len) {
        dead = 0;
    } else {
        inst->beat_index = 0;
        dead = 1;
    }
    inst->sample_len = trunc((float) (inst->beats[inst->beat_index] * sr) / 1000.0);
    inst->sample_phase = inst->sample_len;
    post("increment: index-%d phase-%d beat-%d", inst->beat_index, inst->sample_phase, inst->beats[inst->beat_index]);
    inst->dead = dead;
    return dead;
}

void timebandit_onBangMsg(t_timebandit *x) {
    /*for (short i = 0; i < x->arg_store; i++) {
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
    }
    if (recv(x->socket_desc, x->remote, SOCKET_SIZE, 0) < 0) {
        post("[timebandit~ ]: read from socket %s:%d failed", DEFAULT_IP, DEFAULT_PORT);
    }
    post("%s", x->remote);
    parse_LinkMsg(x);
    close(x->socket_desc);
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
    for (short i = 0; i < argc; i++) {
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

void timebandit_onInstMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv) {
    t_atom *inst_msg = argv;
    if (argc > 2) {
        short i;
        short inst_index = (int) atom_getfloat(inst_msg + 1);
        struct _inst *inst = &x->insts[inst_index]; // the first argument is the instrument index
        
        atom_string(inst_msg + 1, inst->name, inst->name_bytes);
        
        post("%s", x->insts[inst_index].name);
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
    for (short i = 0; i < argc; i++) {
        post("%d", (int) atom_getfloat(scheme_msg+i));
    }
}

void timebandit_free(t_timebandit *x) {
    freebytes(x->arg, x->arg_len);
    freebytes(x->insts, sizeof(struct _inst) * MAX_INSTS);
    freebytes(x->ip, IP_SIZE);
    outlet_free(x->out_metro1);
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
    
    class_addmethod(timebandit_class, (t_method)timebandit_onSchemeMsg, gensym("scheme"), A_GIMME, 0);
    
    post("[timebandit~ ]: http://github.com/ultraturtle0/timebandit.git");
}

void *timebandit_new(void) {
    t_timebandit *x = (t_timebandit *) pd_new(timebandit_class);
    
    x->arg_len = MAX_BEATS * sizeof(int);
    x->arg = (int *) getbytes(x->arg_len);
    
    x->port = DEFAULT_PORT;
    x->ip = getbytes(IP_SIZE);
    x->sample_test = 44100;
    
    x->sr = 44100;

    strcpy(x->ip, DEFAULT_IP);
    
    //x->insts = (struct _inst *) getbytes(sizeof(struct _inst) * MAX_INSTS);
    
    
    inlet_new(&x->obj, &x->obj.ob_pd, gensym("signal"), gensym("signal"));
    struct _inst *inst;
    for(short i = 0; i < MAX_INSTS; i++) {
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
    x->out_metro1 = outlet_new(&x->obj, &s_bang);
    return x;
}

void timebandit_dsp(t_timebandit *x, t_signal **sp) {
    if (x->sr != sp[0]->s_sr && sp[0]->s_sr) { // if sampling rate changes
        x->sr = (int) sp[0]->s_sr;
    }
    dsp_add(timebandit_perform, 5, x, sp[0]->s_vec, sp[1]->s_vec, sp[2]->s_vec, sp[0]->s_n); // pg 29
}

t_int *timebandit_perform(t_int *w) {
    t_timebandit *x = (t_timebandit *) (w[1]);
    //t_float *in = (t_float *) (w[2]);
    //t_float *in2 = (t_float *) (w[3]);
    t_float *out = (t_float *) (w[4]);
    t_int n = w[5];
    
    t_float sig = 0.0;
    //float pre_sig = 0.0;
    
    
    
    struct _inst *inst = &x->insts[0];
    long sample_phase = inst->sample_phase;
    long sample_len = inst->sample_len;
    short the_bang = 0;
    while(n--) {
        //while (! inst->dead) {
            if (! sample_phase--) { // descending phasor samples
                beat_increment(inst, x->sr);
                sample_len = inst->sample_len;
                sample_phase = inst->sample_phase;
                sig = (t_float) 0.0;
                the_bang = 1;
            } else {
        /*if (inst->phase++ >= (x->sr / 1000.0 * (float) inst->beats[inst->beat_index])) {
            inst->phase = 0;
            if (inst->beat_index++ >= inst->beat_len) {
                inst->beat_index = 0;
            }
            post("%d", inst->beats[inst->beat_index]);
        }
        if ((float) inst->beats[inst->beat_index] <= 0.00000001) { // prevent a divide-by-zero error;
            sig = 0.0;
        } else {
            pre_sig = ((float) inst->phase / (float) inst->beats[inst->beat_index] * (float) x->sr / 1000.0 * 2.0) - 1.0; // calc + translate phasor samples
            sig = (pre_sig > 0.000001) ? pre_sig: 0; // prevent computing miniscule signals
        }*/
        /*if (sig >= 1.0 || sig <= -1.0) {
            beat_increment(inst, x->sr);
            post("beat change %d", inst->beats[inst->beat_index]);
            sig = (t_float) 0.0;
        }*/
                sig = (t_float) ((float) sample_phase / (float) sample_len);
            //}
            }
        //}
        //}
        //}
        
        *out++ = sig;
        if (the_bang) {
            outlet_bang(x->out_metro1);
            the_bang = 0;
        }
    }
    inst->sample_phase = sample_phase;
    return w + 6;
    //post("%d", sig);
}
