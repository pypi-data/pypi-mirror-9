/***********************************************************************
**
**   vlapihlp.cpp
**
**   This file is part of libkfrgcs.
**
************************************************************************
**
**   Copyright (c):  2002 by Garrecht Ingenieurgesellschaft
**
**   This file is distributed under the terms of the General Public
**   Licence. See the file COPYING for more information.
**
**   $Id$
**
***********************************************************************/

#include "vlapihlp.h"
#include "utils.h"
#include "Util/StringUtil.hpp"
#include "Util/Macros.hpp"

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

/*
Filtern einer Zeile:
  - Umwandeln von nicht-IGC-Zeichen in Leerzeichen
  - Entfernen von Leer- und Sonderzeichen am Ende (TrimRight)
*/
char *igc_filter(char *st) {
 static constexpr char alphabet[] =
   " \"#%&\'()+-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]_\140abcdefghijklmnopqrstuvwxyz{|}";
 static constexpr int alphabet_l = ARRAY_SIZE(alphabet) - 1;
 int l = strlen(st);
 int i,j;
 int found;
  for(i=0; i<l; i++) {
    found = 0;
    for(j=0; j<alphabet_l; j++)
      if (st[i] == alphabet[j])
	found = 1;
    if (!found) st[i] = ' ';
  }
  TrimRight(st);
  return st;
}

// Aus einer 2byte-Bin�rzahl einen base-36 Seriennummernstring machen
void
wordtoserno(char *Seriennummer, unsigned Binaer)
{
 char SerNStr[4];
 int i,l;
  // limitation
  if (Binaer > 46655L)
    Binaer = 46655L;
  utoa(Binaer,SerNStr,36);
  sprintf(Seriennummer,"%3s",SerNStr);
  // generate leading zeroes
  l = strlen(Seriennummer);
  for (i=0; i<l; i++) {
    if (Seriennummer[i] == ' ')
      Seriennummer[i] = '0';
  };
}



/*
genaue Umrechnung von Druckwert nach H�he.
Druckwert ist ein innerhalb des Loggers temperaturkompensierter Wert, der
proportional zum gemessenen Umgebungsdruck am Logger ist.
1100 mbar entsprechen einem Druckwert von 4096;
*/
long pressure2altitude(unsigned druck) {
double GMR   = 9.80665*28.9644/8314.32;
double tgrad = -6.5E-3;
double p0    = 1013.25;
double p11   = 0.2233611050922 * p0;
double t0    = 288.15;
double t11   = 216.65;
double p;
double hoehe;
 // Umrechnung von normierten ADC-Werten in hPa
 p = 1100.0*druck/4096;
 // Berechnen der Druckh�he anhand des Druckes
 if (p>p11)
   hoehe = (t0 * (exp((tgrad/GMR)*log(p0/p)) - 1) / tgrad);
 else
   hoehe = (t11*log(p11/p)/GMR + 11000);
 return (long int) hoehe;
}



