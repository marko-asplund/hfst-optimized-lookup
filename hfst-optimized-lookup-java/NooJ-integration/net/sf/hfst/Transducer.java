package net.sf.hfst;

import java.io.FileInputStream;
import java.io.DataInputStream;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.util.Collection;

import net.sf.hfst.Transducer;
import net.sf.hfst.UnweightedTransducer;
import net.sf.hfst.WeightedTransducer;
import net.sf.hfst.NoTokenizationException;
import net.sf.hfst.FormatException;

public abstract class Transducer {
    public abstract Collection<String> analyze(String str) throws NoTokenizationException;

    public static Transducer load_binary(String filename) throws IOException
    {
        FileInputStream transducerfile = null;
        transducerfile = new FileInputStream(filename);
        TransducerHeader h = null;
        try { h = new TransducerHeader(transducerfile); }
        catch (FormatException e) {
            System.err.println("File must be in hfst optimized-lookup format");
            return null;
        }
	DataInputStream charstream = new DataInputStream(transducerfile);
	TransducerAlphabet a = new TransducerAlphabet(charstream, h.getSymbolCount());
	if (h.isWeighted()) {
            return new WeightedTransducer(transducerfile, h, a);
        } else {
            return new UnweightedTransducer(transducerfile, h, a);
        }
    }
}
