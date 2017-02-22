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
#include <pthread.h>
#include <fcntl.h>
//#include "tlpi_hdr"

#define MAX_BEATS 1024
#define MAX_INSTS 8

#define DEFAULT_IP          "127.0.0.1"
#define IP_SIZE             16
#define DEFAULT_PORT        8500
#define SOCKET_SIZE         1024
#define PING_SAMPLE_TIME    44100           // how frequently to ping the python server
#define INST_NAME_SIZE      32

#define T_MS                0               // millisecond mode for transport
#define T_SAMP              1               // sample mode for transport
#define T_MARKER            2               // marker mode for transport

#define PAUSE               0               // transport pause
#define PLAY                1               // transport play


static t_class *timebandit_class;

struct _inst {
    int beats[MAX_BEATS];
    short beat_index;
    short beat_len;
    
    long sample_phase;
    float sample_inc;
    long sample_len;
    t_float phase_sig_hold;
    
    int phase;
    float scale;
    char *name;
    unsigned int name_bytes;
    
    int dead;
    int mute;
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
    short inst_len;
    
    pthread_t socket_thread;
    int socket_desc;
    int *socket;
    void *socket_clock;
    short port;
    char *ip;
    unsigned int ip_bytes;
    char remote[SOCKET_SIZE];
    struct sockaddr_in server;
    short state;
    short ping_counter;
    
    short queue;
    
    int transport_ms;
    int transport_samp;
    short transport_mode;
    short transport_status;
} t_timebandit;

void *timebandit_new(void);
void timebandit_dsp(t_timebandit *x, t_signal **sp); // does this need short *count?
void timebandit_onBangMsg(t_timebandit *x);
void timebandit_onLinkMsg(t_timebandit *x);//, t_symbol *msg, short argc, t_atom *argv);
void timebandit_onPortMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv);
void timebandit_onIPMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv);
void timebandit_onTransportMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv);

void timebandit_onStopMsg(t_timebandit *x);
void timebandit_onPlayMsg(t_timebandit *x);
void timebandit_onPauseMsg(t_timebandit *x);

void handshake(t_timebandit *x);
static void *check_socket(void *x);
void testparse(t_timebandit *x);
void transport_reset(t_timebandit *x);
void dispatcher(t_timebandit *x);

void parse_LinkMsg(t_timebandit *x);
void parse_Inst(t_timebandit *x, char *remote);
void parse_Beats(struct _inst *inst, char *remote);

int dp_Play(t_timebandit *x);
int dp_Pause(t_timebandit *x);
int dp_Stop(t_timebandit *x);
int dp_Transport(t_timebandit *x, int ms);
int dp_Inst(t_timebandit *x, char *args);

int beat_increment(struct _inst *inst, int sr);

t_int *timebandit_perform(t_int *w);

void *check_socket(void *x) {
    int *oldstate;
    int *oldtype;
    pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, oldstate);
    pthread_setcanceltype(PTHREAD_CANCEL_DEFERRED, oldtype);
    
    t_timebandit *tb = (t_timebandit *) x;
    
    int socket_desc;
    char comm[SOCKET_SIZE];
    struct sockaddr_in server;
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_desc == -1) {
        post("[timebandit~ ]: error creating socket");
    }
    tb->socket = &socket_desc;
    
    server.sin_addr.s_addr = inet_addr(tb->ip);
    server.sin_family = AF_INET;
    server.sin_port = htons(tb->port);
    
    if (connect(socket_desc, (struct sockaddr *) &server, sizeof(server)) < 0) {
        post("[timebandit~ ]: error connecting to remote server");
        tb->state = 0;
    } else {
        send(socket_desc, "ready", sizeof("ready"), 0);
        
        fcntl(socket_desc, F_SETFL, 0);
        tb->state = 1;
        
        memset(comm, 0, SOCKET_SIZE);
        //char *test[1024];
        while (1) {
            memset(comm, 0, sizeof(comm));
            if (recv(socket_desc, comm, SOCKET_SIZE, 0) < 0) {
                post("[timebandit~ ]: read from socket %s:%d failed", DEFAULT_IP, DEFAULT_PORT);
            } else {
                // PUT A QUEUE HERE LATER
                if (strcmp(comm, "standby")) {
                    // MUTEX HERE?
                    tb->queue = 1;
                    strcpy(tb->remote, comm);
                    
                } else {
                    tb->queue = 0;
                }
                
                //send(socket_desc, "ready", sizeof("ready"), 0);
            }
        }
    }
    
    return NULL;
}

void dispatcher(t_timebandit *x) {
    //post("incoming: %s", x->remote);
    x->queue--;
    char *comm = x->remote;
    char *args;
    const char *command_delim = " ";
    char *lasts;
    int err = 0;
    comm = strtok_r(comm, command_delim, &lasts);
    args = strtok_r(NULL, command_delim, &lasts);
    post("command: %s, args: %s", comm, args);
    
    if (! strcmp(comm, "inst")) {
        err = dp_Inst(x, args);
    } else if (! strcmp(comm, "play")) {
        timebandit_onPlayMsg(x);
    } else if (! strcmp(comm, "transport")) {
        err = dp_Transport(x, (int) strtol(args, NULL, 0));
    } else if (! strcmp(comm, "pause")) {
        timebandit_onPauseMsg(x);
    } else if (! strcmp(comm, "stop")) {
        timebandit_onStopMsg(x);
    }
    if (err < 0) {
        post("[timebandit~ ]: remote usage error: %s", comm);
    }
}

int dp_Inst(t_timebandit *x, char *args) {
    char *token;
    char *tofree, *arg;
    tofree = arg = strdup(args);
    int i;
    int index = (int) strtol((token = strsep(&arg, " ")), NULL, 0);
    
    struct _inst *inst;
    
    if (index < MAX_INSTS && index >= 0) {
        inst = &x->insts[index];
    } else {
        free(tofree);
        return 1;
    }
    while ((token = strsep(&arg, " "))) {
        index = (int) strtol(token, NULL, 0);
        inst->beats[inst->beat_len++] = index;
    }
    post("added to inst:");
    for (i = 0; i < inst->beat_len; i++) {
        post("beat %d: %d", i, inst->beats[i]);
    }
    inst->dead = 0;
    inst->beat_index = inst->beat_len;
    beat_increment(inst, x->sr);
    free(tofree);
    return 0;
}



int dp_Transport(t_timebandit *x, int ms) {
    x->transport_ms = ms;
    x->transport_samp = (float) (x->sr * ms) / 1000.0;
    transport_reset(x);
    return 0;
}

int dp_Pause(t_timebandit *x) {
    return 0;
}

int dp_Stop(t_timebandit *x) {
    return 0;
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

void newparse_LinkMsg(t_timebandit *x) {
    char *remote = x->remote;
    const char *command_delim = ":";
    char *lasts;
    char *token;
    
    token = strtok_r(remote, command_delim, &lasts);
    //if (strcmp(<#const char *#>, <#const char *#>))
    while(token) { //loop each command
        post("command: %s", token);
        parse_Inst(x, token);
        token = strtok_r(NULL, command_delim, &lasts);
    }
}

void testparse(t_timebandit *x) {
    char *remote = x->remote;
    if (! strcmp(remote, "hooray it works")) {
        post("whoopee it doubly works!");
    } else if (! strcmp(remote, "standby")) {
        post("standing by, baby");
    }
}

int beat_increment(struct _inst *inst, int sr) {
    int dead;
    if (inst->beat_index++ <= inst->beat_len) {
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
    post("helloworld");
}

void timebandit_onLinkMsg(t_timebandit *x) {
    int err = pthread_create(&x->socket_thread, NULL, check_socket, x);
    if (err != 0) {
        post("[timebandit~ ]: unable to initialize client thread");
    }
    x->state = 1;
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

void transport_reset(t_timebandit *x) {
    // set beat indices and phases
    short i;
    int goal = x->transport_ms;
    struct _inst *inst;
    int accum;
    int last_accum = 0;
    short b = 0;
    for (i = 0; i < MAX_INSTS; i++) {
        post("we are on inst %d", i);
        inst = &x->insts[i];
        accum = 0;
        last_accum = 0;
        post("beatlen %d", inst->beat_len);
        for (b = 0; b < inst->beat_len; b++) {
            post("starting beat %d...", b);
            accum += inst->beats[b];
            post("accum %d", accum);
            if (accum > goal) { // need to check for equality?
                post("okay we passed it. goal: %d", goal);
                inst->beat_index = b;
                inst->sample_len = trunc(((float) (inst->beats[b] * x->sr)) / 1000.0);
                
                //post("calculating placement within beat: %d - %d", last_accum, x->transport_samp);
                inst->sample_phase = inst->sample_len - last_accum;
                post("sample_len %d phase %d last_accum %d", inst->sample_len, inst->sample_phase, last_accum);
                inst->dead = 0;
                break;
            }
            last_accum = accum;
            if (b == inst->beat_len - 1) { // last time, check if dead
                post("[timebandit~ ]: transport exceeded inst length by %d ms", goal - accum);
                inst->dead = 1;
            }
        }
        //post("sample_len %d phase %d", inst->sample_len, inst->sample_phase);
    }
}

void timebandit_onStopMsg(t_timebandit *x) {
    x->transport_status = PAUSE;
    short i;
    
    long beat;
    struct _inst *inst;
    for (i = 0; i < MAX_INSTS; i++) {
        inst = &x->insts[i];
        inst->beat_index = 0;
        inst->dead = 0;
        inst->phase_sig_hold = 0.0;
        beat = inst->beats[0];
        inst->sample_len = trunc((float) (beat * x->sr) / 1000.0);
        inst->sample_phase = inst->sample_len;
        post("len %d beats %d phase %d", inst->sample_len, inst->beats[0], inst->sample_phase);
    }
}

void timebandit_onPlayMsg(t_timebandit *x) {
    x->transport_status = PLAY;
}

void timebandit_onPauseMsg(t_timebandit *x) {
    x->transport_status = PAUSE;
    struct _inst *inst;
    short i;
    for (i = 0; i < MAX_INSTS; i++) {
        inst = &x->insts[i];
        inst->phase_sig_hold = (t_float) ((float) inst->sample_phase / (float) inst->sample_len);
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
            
            inst->beat_len++;
            post("%d", x->insts[inst_index].beats[i - 2]);
        }
        inst->dead = 0;
        inst->beat_index = inst->beat_len;
        beat_increment(inst, x->sr);
        post("%d, %d, %d", inst->beat_index, inst->sample_phase, inst->sample_len);
    }
}

void timebandit_onTransportMsg(t_timebandit *x, t_symbol *msg, short argc, t_atom *argv) {
    if (argc < 2) {
        post("[timebandit~ ]: transport command requires arguments <unit> <time>");
        return;
    }
    float transport_var = atom_getfloat(argv + 1);
    float t_ms = 0.0;
    float t_samp = 0.0;
    char *unit[8];
    atom_string(argv, *unit, 8);
    
    
    if (! strcmp(*unit, "ms")) {
        t_ms = 1.0;
        t_samp = (float) x->sr / 1000.0; // do these calculations when sample rate changes instead of every time
    }
    if (! strcmp(*unit, "samp")) {
        t_ms = 1000.0 / (float) x->sr;
        t_samp = 1.0;
    }
    x->transport_ms = (int) (transport_var * t_ms);
    x->transport_samp = (int) (transport_var * t_samp);
    transport_reset(x);
}

void timebandit_free(t_timebandit *x) {
    void *res; // thread status
    if (x->state) {
        close(*x->socket);
        pthread_cancel(x->socket_thread);
        pthread_join(x->socket_thread, &res);
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
    class_addmethod(timebandit_class, (t_method)timebandit_onInstMsg, gensym("inst"), A_GIMME, 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onPortMsg, gensym("port"), A_GIMME, 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onIPMsg, gensym("ip"), A_GIMME, 0);

    class_addmethod(timebandit_class, (t_method)timebandit_onTransportMsg, gensym("transport"), A_GIMME, 0);
    
    class_addmethod(timebandit_class, (t_method)timebandit_onPlayMsg, gensym("play"), 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onPauseMsg, gensym("pause"), 0);
    class_addmethod(timebandit_class, (t_method)timebandit_onStopMsg, gensym("stop"), 0);
    
    post("[timebandit~ ]: http://github.com/ultraturtle0/timebandit.git");
}

void *timebandit_new(void) {
    t_timebandit *x = (t_timebandit *) pd_new(timebandit_class);
    
    x->arg_len = MAX_BEATS * sizeof(int);
    x->arg = (int *) getbytes(x->arg_len);
    
    x->port = DEFAULT_PORT;
    x->ip = getbytes(IP_SIZE);
    x->ping_counter = PING_SAMPLE_TIME;
    x->state = 0;
    x->sample_test = 44100;
    x->queue = 0;
    memset(x->remote, 0, SOCKET_SIZE);
    
    x->transport_ms = 0;
    x->transport_samp = 0;
    x->transport_mode = T_MS;
    x->transport_status = PAUSE;
    
    x->sr = 44100;
    
    strcpy(x->ip, DEFAULT_IP);
    x->socket_clock = clock_new(x, (t_method) dispatcher);
    
    inlet_new(&x->obj, &x->obj.ob_pd, gensym("signal"), gensym("signal"));
    struct _inst *inst;
    x->inst_len = 0;
    short i;
    for(i = 0; i < MAX_INSTS; i++) {
        inst = &x->insts[i];
        inst->name = getbytes(INST_NAME_SIZE);
        inst->beat_index = 0;
        inst->beat_len = 0;
        inst->phase = 0;
        inst->sample_phase = 44100;
        inst->sample_len = inst->sample_phase;
        inst->phase_sig_hold = 0.0;
        inst->dead = 1;
        inst->mute = 0;
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
    
    short o;
    for (o = 0; o < MAX_INSTS; o++) {
        x->outs[o] = (t_float *) (w[o + 4]);
    }
    
    t_int n = w[12];
    
    t_float sig = 0.0;
    
    struct _inst *inst;
    long sample_phase;
    long sample_len;
    short the_bang = 0;
    short ping_counter = x->ping_counter;
    
    while(n--) {
        if ((! ping_counter--) && (x->queue)) {
            clock_delay(x->socket_clock, 0);
        }
        if (x->transport_status == PLAY) {
            //while (! inst->dead) {
            
            for (o = 0; o < MAX_INSTS; o++) {
                inst = &x->insts[o];
                if (! inst->dead) {
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
                    
                    
                    if (the_bang) {
                        outlet_bang(x->out_metro[o]);
                        //clock_delay(bang_clock(x->out_metro[o]), 0);
                        the_bang = 0;
                    }
                    inst->sample_phase = sample_phase;
                    inst->sample_len = sample_len;
                } else if (inst->mute) {
                    sig = (t_float) 0.0;
                } else {
                    sig = (t_float) -1.0;
                }
                *x->outs[o]++ = sig;
            }
        } else {
            for (o = 0; o < MAX_INSTS; o++) {
                inst = &x->insts[o];
                *x->outs[o]++ = inst->phase_sig_hold;
            }
        }
    }
    x->ping_counter = ping_counter;
    return w + 13;
}

