import numpy as np

class Rdf:

    def __init__( self, max_r, number_of_bins ):
        self.max_r = max_r
        self.number_of_bins = number_of_bins
        self.data = np.zeros( number_of_bins )
        self.dr = max_r / number_of_bins
 
    def add_dr( self, dr ):
        this_bin = int( dr / self.dr ) 
        if this_bin > self.number_of_bins:
            raise IndexError( 'dr is larger than rdf max_r' )
        self.data[ this_bin ] += 1

    def normalised_data( self ):
        return( np.array( [ [ dr, g_of_r / self.volume_factor( dr ) ] for dr, g_of_r in zip( np.array( [ self.dr * ( r + 0.5 ) for r in range( 0, self.number_of_bins ) ] ), self.data / np.sum( self.data ) ) ] ) )  

    def __add__( self, other_rdf ):
        assert isinstance( other_rdf, Rdf )
        assert self.max_r == other_rdf.max_r
        assert self.number_of_bins == other_rdf.number_of_bins
        summed_rdf = Rdf( self.max_r, self.number_of_bins )
        summed_rdf.data = self.data + other_rdf.data
        return summed_rdf 

    def volume_factor( self, dr ):
        return ( ( dr + self.dr )**3 - dr**3 )
