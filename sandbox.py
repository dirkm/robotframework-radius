import pyrad.dictionary
import pyrad.packet


dictionary = pyrad.dictionary.Dictionary('dictionary')
pkt = pyrad.packet.AuthPacket(secret='avcd',dict=dictionary)
