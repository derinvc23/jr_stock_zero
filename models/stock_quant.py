from odoo import fields, models,api


class ProductProduct(models.Model):
    _inherit = "product.template"
    
    location_ids1=fields.Many2many("stock.location",string="Ubicaciones")

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    location_ids1=fields.Many2many("stock.location", string="Ubicaciones",store=True,compute="_get_location")

    @api.depends("product_tmpl_id.location_ids1")
    def _get_location(self):
        for line in self:
            if line.product_tmpl_id.location_ids1:
                line.location_ids1=line.product_tmpl_id.location_ids1
            else:
                line.location_ids1=False

class StockZero(models.TransientModel):
    _name = "stockzero"
    _description = "reporte stock zero"

    
    locations_ids = fields.Many2many(
        "stock.location",
        string="Ubicacion",
    )
   
    tipo_stock=fields.Selection([
        ("z","Stock Zero"),
        ("p","Stock con existencia"),
        ("t","Todos"),],string="Tipo de reporte")

    

    
    
  

    def generate(self):
        report = self.env.ref("jr_stock_zero.stock_summary_report")
        return self.env['report'].get_action(self,"jr_stock_zero.comercial")

    def get_orders(self):
        if self.tipo_stock=="z":
            obj = self.env["product.product"].search(
                [
                    ("location_ids1", "in", self.locations_ids.ids),
                    ("qty_available","<=",0),
                   
                ]
            )
            orders=[]

            for line in obj:
                for record in line.location_ids1:
                    orders.append([record.name,line.default_code,line.name,line.qty_available])

        elif self.tipo_stock=="p":
            obj= self.env["stock.quant"].search(
                [
                    ("location_id", "in", self.locations_ids.ids),
                    
                ]
            )
            
            orders=[]
            for line in obj:
                if not orders:
                    orders.append([line.location_id.name,line.product_id.default_code,line.product_id.name,line.qty])
                else:
                    for record in orders:
                        if line.product_id.default_code== record[1] and line.location_id.name==record[0]:
                            record[2]=record[2]+line.qty


   

            

        elif self.tipo_stock=="t":
            product= self.env["product.product"].search(
                [
                    ("location_ids1", "in", self.locations_ids.ids),
                    ("qty_available","<=",0),
                   
                ]
            )

            quant1 = self.env["stock.quant"].search(
                [
                    ("location_id", "in", self.locations_ids.ids),
                    
                ]
            )

            orders1=[]
            for line in product:
                for record in line.location_ids1:
                    orders1.append([record.name,line.default_code,line.name,line.qty_available])

            quant=[]
            for line in quant1:
                if not quant:
                    quant.append([line.location_id.name,line.product_id.default_code,line.product_id.name,line.qty])
                else:
                    for record in quant:
                        if line.product_id.default_code== record[1] and line.location_id.name==record[0]:
                            record[2]=record[2]+line.qty
            
            orders=orders1+quant

        return orders
    
    def get_orders1(self):
        if self.tipo_stock=="z":
            obj = self.env["product.product"].search([
    ("location_ids1", "in", self.locations_ids.ids),
    ("qty_available","<=",0),
            ])
            orders = []
            for line in obj:
                for record in line.location_ids1:
                    orders.append([record.name,line.default_code,line.name,line.qty_available])

            

        elif self.tipo_stock=="p":
            quants= self.env["stock.quant"].search(
                [
                    ("location_id", "in", self.locations_ids.ids),
                ]
            )
            
            orders={}
            for quant in quants:
                key=(quant.location_id.id,quant.product_id.id)
                if key not in orders:
                    orders[key]=[quant.location_id.name,quant.product_id.default_code,quant.product_id.name,quant.qty]
                else:
                    orders[key][3]+=quant.qty
            
            for order in orders.values():
                orders.append(order)

        elif self.tipo_stock=="t":
            products= self.env["product.product"].search(
                [
                    ("location_ids1", "in", self.locations_ids.ids),
                    ("qty_available","<=",0),
                ]
            )

            quants= self.env["stock.quant"].search(
                [
                    ("location_id", "in", self.locations_ids.ids),
                ]
            )

            orders=[]
            for product in products:
                for record in product.location_ids1:
                    orders.append([record.name,product.default_code,product.name,product.qty_available])

            for quant in quants:
                key=(quant.location_id.id,quant.product_id.id)
                if key not in orders:
                    orders[key]=[quant.location_id.name,quant.product_id.default_code,quant.product_id.name,quant.qty]
                else:
                    orders[key][3]+=quant.qty
            
            for order in orders.values():
                orders.append(order)

        return orders


