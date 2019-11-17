from django.shortcuts import render
from rango.models import Category
from rango.models import Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserProfileForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime
from rango.webhose_search import run_query
from registration.backends.simple.views import RegistrationView


class MyRegistrationView(RegistrationView):
    # 自定义一个类，覆盖 registration.backends.simple.views 提供的 RegistrationView
    # 用户注册成功后重定向
    def get_success_url(self, user=None):
        return reverse('rango:register_profile')


def index(request):
    # 查询数据库，获取目前存储的所有分类
    # 按点赞次数倒序排列分类
    # 获取前5个分类（如果分类数少于5个，那就获取全部）
    # 把分类列表放入 context_dict 字典
    # 稍后传给模板引擎

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,
                    'pages': page_list}

    # 调用处理 cookie 的辅助函数
    # print('======>: ' + datetime.now().strftime('%Y%m%d%H%M%S'))
    visitor_cookie_handle(request)
    context_dict['visits'] = request.session['visits']

    # 返回
    response = render(request, 'rango/index.html', context_dict)
    return response


def about(request):

    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

    # 打印请求方法
    print(request.method)
    # 打印用户名
    print(request.user)
    context_dict = {'message': "This tutorial has been put together by <your-name>.",
                    'visits': request.session['visits']}
    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    # 创建上下文字典，稍后传给模板渲染引擎
    context_dict = {}

    try:
        # 能通过传入的分类别名找到对应的分类吗？
        # 如果找不到，.get() 方法抛出 DoesNotExist 异常
        # 因此 .get() 方法返回一个模型实例或者抛出异常
        category = Category.objects.get(slug=category_name_slug)

        # 检索关联的所有网页
        # 注意， filter()返回一个网页对象列表或者空列表
        pages = Page.objects.filter(category=category)

        # 把得到的列表赋值给模板上下文中名为 pages 的键
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['query'] = query
    context_dict['result_list'] = result_list

    # 渲染响应，返回给客户端
    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    form = CategoryForm()
    # 是 HTTP POST 请求吗
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # 表单数据有效吗
        if form.is_valid():
            # 把新分类存入数据库
            form.save(commit=True)
            # 保存新分类后可以显示一个确认消息
            # 不过既然最受欢迎的分类在首页
            # 那就把用户带到首页吧
            return index(request)
        else:
            # 表单数据有错误
            # 直接在终端里打印出来
            print(form.errors)
    # 处理有效和无效数据后之后
    # 渲染表单，并显示可能出现的错误消息
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        # 通过 category_name_slug 在数据库中 category
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()
            return show_category(request, category_name_slug)
        else:
            print(form.errors)

    print(form.is_valid())
    print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    # 一个布尔值，告诉模板注册是否成功
    # 一开始设为 False， 注册成功后改为 True
    registered = False

    # 如果是 HTTP POST 请求，处理表单数据
    if request.method == 'POST':
        # 尝试获取原始表单数据
        # 注意，UserForm 和 UserProfileForm 中的数据都需要
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # 如果两个表单中的数据是有效的
        if user_form.is_valid() and profile_form.is_valid():
            # 把 UserForm 中的数据存入数据库
            user = user_form.save()

            # 使用 set_password 方法计算密码哈希值
            # 然后更行 user 对象
            user.set_password(user.password)
            user.save()

            # 现在处理 UserProfile 实例
            # 因为要自行处理 user 属性，所以设定 commit=False
            # 延迟保存模型，以防出现完整性问题
            profile = profile_form.save(commit=False)
            profile.user = user

            # 用户提供了头像了吗
            # 如果提供了，从表单数据库中提取出来， 赋给UserProfile 模型
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # 保存实例
            profile.save()

            # 更新变量的值，告诉模板注册成功了
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        # 不是 POST 请求， 渲染两个 ModelForm 实例
        # 表单为空，待用户填写
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return HttpResponseRedirect(reverse('rango:index'))
        else:
            print(form.errors)

    context_dict = {'form': form}

    return render(request, 'rango/profile_registration.html', context_dict)


def user_login(request):
    # 如果是 HTTP POST 请求，尝试提取相关信息
    if request.method == 'POST':
        # 获取用户在登陆表单中输入的用户名和密码
        # 我们使用的是 request.POST.get('<variable>')
        # 而不是 request.POST['<>']
        # 而后者抛 KeyError 异常
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 使用 Django 提供的函数检查 username/password 是否有效
        # 如果有效，返回一个 User 对象
        user = authenticate(username=username, password=password)

        # 如果得到了 User 对象，说明用户输入的凭据是对的
        # 如果是 None (Python 表示没有值得方式)，说明没找到与凭据匹配的用户
        if user:
            # 账户是否激活，或者被禁了
            if user.is_active:
                # 登入有效并且已经激活的账户
                # 然后重定向到首页
                login(request, user)
                return HttpResponseRedirect(reverse('rango:index'))
            else:
                # 未激活
                return render(request, 'rango/login.html', {})
        else:
            # 提供的登陆凭证无效
            print("Invalid login details: {0}, {1}".format(username, password))
            return render(request, 'rango/login.html', {})
    else:
        # 不是 POST 请求，显示登陆表单
        return render(request, 'rango/login.html', {})


# 装饰器模式
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


# 装饰器限制，只有登陆了的用户才能访问这个试图
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('rango:index'))


# 辅助函数
def get_server_side_cookie(request, cookie_name, default_val=None):
    val = request.session.get(cookie_name)
    if not val:
        val = default_val
    return val


def visitor_cookie_handle(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    # 如果距上次访问已超过一天
    if (datetime.now() - last_visit_time).seconds > 10:
        visits += 1
        # 更新
        # response.set_cookie('last_visit', str(datetime.now()))
        request.session['last_visit'] = str(datetime.now())
    else:
        # response.set_cookie('last_visit', last_visit_cookie)
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits


def search(request):

    result_list = []
    query = ''
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})


def track_url(request):
    page_id = None
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            page = Page.objects.get(id=page_id)
            page.views += 1
            page.save()
            print('page.views: %d' % page.views)
            return HttpResponseRedirect(page.url)
    return HttpResponseRedirect(reverse('rango:index'))


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('rango:index'))

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {'website': userprofile.website, 'picture': userprofile.picture})

    if request.method == 'POST' and request.user.id == userprofile.user.id:
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid:
            form.save(commit=True)
            return HttpResponseRedirect(reverse('rango:profile', kwargs={'username': user.username}))
        else:
            print(form.errors)

    return render(request, 'rango/profile.html', {'userprofile': userprofile,
                                                 'selecteduser': user,
                                                  'form': form})


@login_required
def like_category(request):
    cat_id = None
    print("=====>>>")
    if request.method == 'GET' and 'category_id' in request.GET:
        cat_id = request.GET['category_id']
    likes = 0
    if cat_id:
        category = Category.objects.get(id=cat_id)
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()
    return HttpResponse(likes)


def test_html(request):
    return render(request, 'rango/my_test.html', {})


def get_category_list(max_results=0, starts_with=''):
    max_results = (max_results if (max_results > 0) else 0)
    result_list = []
    if starts_with:
        result_list = Category.objects.filter(name__istartswith=starts_with)[:max_results]
    return result_list


def suggest_category(request):
    starts_with = ''
    if request.method == 'GET':
        if 'suggestion' in request.GET:
            starts_with = request.GET['suggestion']
    cat_list = get_category_list(8, starts_with)

    return render(request, 'rango/cats.html', {'cats': cat_list})


@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category,
                                           title=title,
                                           url=url,
                                           first_visit=datetime.now(),
                                           last_visit=datetime.now())
            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['pages'] = pages

    return render(request, 'rango/page_list.html', context_dict)


