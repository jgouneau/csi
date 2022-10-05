from msilib.schema import Error


class Model:
    """
    Classe permettant la simulation d'une compression d'un objet 3D suivant l'algorithme SQUEEZE 
    """

    def __init__():
        None

    def load_M(self, model):
        """Load le model initial.

        Args:
            model (_type_): _description_
        """
        None

    def deletion(self):
        """Renvoie les infos de la prochaine arête à supprimer et la supprime.

        Raises:
            Error: S'il n'y a plus d'arêtes à supprimer ; il faut alors appeler get_m0.

        Returns:
            dict: Contient :
                ``i_del``: l'indice du sommet supprimé
                ``v_del``: les coordonnées du sommet supprimé
                ``f_del``: tuple des deux faces supprimées
                ``f_modified`` : liste des faces modifiées 
        """
        if 1 == 0:
            raise ValueError
        result = dict(
            i_del=None,
            v_del=None,
            f_del=(None, None),
            f_modified=list(None),
        )
        return result

    def get_M0(self):
        """Retourne le model simplifié.

        Returns:
            _type_: _description_
        """
        M0 = None
        return M0