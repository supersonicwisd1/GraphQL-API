import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models.user import User as UserModel
from models.fb_account import FBAccount as FBAccountModel
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models.fb_engagement import FBEngagement as FBEngagementModel
from datetime import datetime, timedelta


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node,)

class CreateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        email = graphene.String()
        password = graphene.String()

    user = graphene.Field(lambda: User)

    def mutate(self, info, name, email, password):
        user = UserModel(name=name, email=email, password=password)
        db.add(user)
        db.commit()
        return CreateUser(user=user)

class Mutations(graphene.ObjectType):
    create_user = CreateUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutations)

class FBAccount(SQLAlchemyObjectType):
    class Meta:
        model = FBAccountModel
        interfaces = (relay.Node,)

class Query(graphene.ObjectType):
    all_fb_accounts = graphene.List(FBAccount)
    fb_account = graphene.Field(FBAccount, user_id=graphene.Int())
    
    def resolve_all_fb_accounts(self, info):
        query = FBAccount.get_query(info)
        return query.filter(FBAccountModel.is_active==True).all()
    
    def resolve_fb_account(self, info, user_id):
        query = FBAccount.get_query(info)
        return query.filter(FBAccountModel.user_id == user_id, FBAccountModel.is_active==True).first()


class FBEngagement(SQLAlchemyObjectType):
    class Meta:
        model = FBEngagementModel
        interfaces = (relay.Node,)

class Summary(graphene.ObjectType):
    total_likes = graphene.Int()
    total_shares = graphene.Int()
    total_comments = graphene.Int()

class Query(graphene.ObjectType):
    fb_engagements = graphene.List(lambda: FBEngagement, user_id=graphene.Int())
    summary = graphene.Field(lambda: Summary, user_id=graphene.Int())

    def resolve_fb_engagements(self, info, user_id):
        query = FBEngagement.get_query(info)
        return query.filter(FBEngagementModel.user_id == user_id, FBEngagementModel.date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), FBEngagementModel.date < datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)).order_by(FBEngagementModel.date.desc()).all()
    
    def resolve_summary(self, info, user_id):
        query = FBEngagement.get_query(info)
        result = query.filter(FBEngagementModel.user_id == user_id, FBEngagementModel.date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), FBEngagementModel.date < datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)).all()
        total_likes = 0
        total_shares = 0
        total_comments = 0
        for engagement in result:
            total_likes += engagement.likes
            total_shares += engagement.shares
            total_comments += engagement.comments
        return Summary(total_likes=total_likes, total_shares=total_shares, total_comments=total_comments)
