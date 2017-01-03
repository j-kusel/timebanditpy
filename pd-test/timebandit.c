//
//  timebandit.c
//  timebandit
//
//  Created by Jordan Kusel on 1/1/17.
//  Copyright © 2017 jordankusel. All rights reserved.
//

#include "m_pd.h"

static t_class *timebandit_class;

typedef struct _timebandit {
    t_object    x_obj;
    t_int       init_count, current_count;
    t_int       mod_A, mod_B;
    t_inlet     *in_mod_A, *in_mod_B;
    t_outlet    *out_A, *out_B, *out_sync, *out_count;
}t_timebandit;

void timebandit_setMods(t_timebandit *x, t_floatarg f1, t_floatarg f2){
    x->mod_A = (f1 <= 0) ? 1 : f1;
    x->mod_B = (f2 <= 0) ? 1 : f2;
}

void timebandit_resetCount(t_timebandit *x){
    x->init_count = 0;
    x->current_count = x->init_count;
}

void timebandit_onBangMsg(t_timebandit *x){
    post("helloworld");
    t_int mod_A         = x->mod_A;
    t_int mod_B         = x->mod_B;
    t_int mod_sync      = mod_A * mod_B;
    t_int n             = x->current_count;
    
    if(n % mod_sync == 0){
        outlet_bang(x->out_A);
        outlet_bang(x->out_B);
        outlet_bang(x->out_sync);
        
        x->current_count = 0;
    } else {
        if(n % mod_A == 0) outlet_bang(x->out_A);
        if(n % mod_B == 0) outlet_bang(x->out_B);
    }
    
    outlet_float(x->out_count, x->current_count);
    x->current_count++;
    
    
    
}

void timebandit_onResetMsg(t_timebandit *x){
    timebandit_resetCount(x);
}

void timebandit_onListMsg(t_timebandit *x, t_symbol *s, t_int argc, t_atom *argv){
    switch(argc){
        case 2:
            timebandit_setMods(x, atom_getfloat(argv), atom_getfloat(argv+1));
            timebandit_resetCount(x);
            break;
        default:
            error("[timebandit ]: two arguments are needed to set a new ratio");
    }
}

void timebandit_onSet_A(t_timebandit *x, t_floatarg f){
    timebandit_setMods(x, f, x->mod_B);
}

void timebandit_onSet_B(t_timebandit *x, t_floatarg f){
    timebandit_setMods(x, x->mod_A, f);
}

void *timebandit_new(t_floatarg f1, t_floatarg f2){
    t_timebandit *x = (t_timebandit *)pd_new(timebandit_class);
    timebandit_resetCount(x);
    timebandit_setMods(x, f1, f2);
    
    x->in_mod_A = inlet_new(&x->x_obj, &x->x_obj.ob_pd, &s_float, gensym("ratio_A"));
    x->in_mod_B = inlet_new(&x->x_obj, &x->x_obj.ob_pd, &s_float, gensym("ratio_B"));
    
    x->out_A = outlet_new(&x->x_obj, &s_bang);
    x->out_B = outlet_new(&x->x_obj, &s_bang);
    x->out_sync = outlet_new(&x->x_obj, &s_bang);
    x->out_count = outlet_new(&x->x_obj, &s_float);
    return (void *)x;
}

void timebandit_free(t_timebandit *x){
    inlet_free(x->in_mod_A);
    inlet_free(x->in_mod_B);
    
    outlet_free(x->out_A);
    outlet_free(x->out_B);
    outlet_free(x->out_sync);
    outlet_free(x->out_count);
}

void timebandit_setup(void){
    timebandit_class = class_new(gensym("timebandit"),
                                 (t_newmethod)timebandit_new,
                                 (t_method)timebandit_free,
                                 sizeof(t_timebandit),
                                 CLASS_DEFAULT,
                                 A_DEFFLOAT, //A of A:B
                                 A_DEFFLOAT, //B of B:A
                                 0);
    class_sethelpsymbol(timebandit_class, gensym("timebandit"));
    
    class_addbang(timebandit_class, (t_method)timebandit_onBangMsg);
    
    class_addlist(timebandit_class, (t_method)timebandit_onListMsg);
    
    class_addmethod(timebandit_class,
                    (t_method)timebandit_onResetMsg,
                    gensym("reset"),
                    0);
    
    class_addmethod(timebandit_class,
                    (t_method)timebandit_onSet_A,
                    gensym("ratio_A"),
                    A_DEFFLOAT,
                    0);
    
    class_addmethod(timebandit_class,
                    (t_method)timebandit_onSet_B,
                    gensym("ratio_B"),
                    A_DEFFLOAT,
                    0);
}
